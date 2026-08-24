import os

# Disable tqdm progress bars in background worker threads to prevent Windows stderr flush errors
os.environ["TQDM_DISABLE"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import re
import torch
import librosa
import numpy as np
from typing import Optional
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Whisper processes audio in 30-second windows at 16kHz
WHISPER_SAMPLE_RATE  = 16000
WHISPER_CHUNK_LENGTH = 30                                   # seconds
WHISPER_N_SAMPLES    = WHISPER_SAMPLE_RATE * WHISPER_CHUNK_LENGTH  # 480,000 samples

# Day 10: PRD latency target
PRD_LATENCY_TARGET_SEC = 2.5

# ═══════════════════════════════════════════════════════════════════════════
# Arabic/Urdu diacritical marks and extended characters that are NEVER
# standalone meaningful tokens — if they appear as isolated tokens or in
# dense sequences, it's hallucination garbage.
# ═══════════════════════════════════════════════════════════════════════════
_ARABIC_DIACRITICS = set("ًٌٍَُِّْٰٕٖٓٔٗ٘ٙٚ")
_ARABIC_EXTENDED_CHARS = set("ٮٯٱٲٳٴٵٶٷٸٹٺٻټٽٿ")

# Common 1-2 char Urdu/Arabic words that are LEGITIMATE (don't flag these as gibberish)
_LEGIT_SHORT_URDU = {
    "کو", "ہے", "اور", "بھی", "اس", "کا", "کی", "کے", "نے", "سے", "پر",
    "تو", "جو", "یہ", "وہ", "ان", "اب", "جب", "تب", "نہ", "ہی", "میں",
    "ہم", "ہو", "دو", "یا", "آج", "کم", "بن", "آپ", "گی", "دن",
}

# Initial prompt to guide Whisper's transcription — conditions the model to
# expect medical dictation with drug names, dosages, and clinical terms.
WHISPER_INITIAL_PROMPT = (
    "Medical prescription dictation. Patient symptoms, medicines like Panadol, "
    "Augmentin, Brufen, Cefspan, Ponstan, Flagyl, Disprin, Risek, Arinac. "
    "Dosages in mg. Frequency like 3 times a day, 2 times a day. Duration in days. "
    "Recheckup follow-up advice."
)


def _clean_hallucinated_repetitions(text: str) -> str:
    """
    Detects and removes Whisper hallucination loops where the same word or short
    phrase is repeated many times consecutively (e.g. "علمہ علمہ علمہ علمہ ...").
    """
    if not text or len(text) < 20:
        return text

    # Phase 1: Collapse single-word repetitions (5+ consecutive identical words)
    cleaned = re.sub(r'\b(\S+)(?:\s+\1){4,}\b', r'\1', text)

    # Phase 2: Collapse 2-word phrase repetitions (4+ consecutive)
    cleaned = re.sub(r'((?:\S+\s+){1,2}\S+)(?:\s+\1){3,}', r'\1', cleaned)

    # Phase 3: If the result is suspiciously short after cleaning (just 1-2 words
    # that were repeated), it was likely pure hallucination — return empty
    words_after = cleaned.split()
    if len(words_after) <= 2 and len(text.split()) > 20:
        return ""

    return cleaned.strip()


def _clean_character_soup_hallucination(text: str) -> str:
    """
    Detects and removes Whisper 'character soup' hallucinations where the model
    outputs random isolated characters, diacritics, and nonsense tokens.
    
    Uses a sliding window of 10 tokens. If >= 6 tokens are 'garbage', truncate.
    """
    if not text:
        return text

    tokens = text.split()
    if len(tokens) < 12:
        return text

    def _is_garbage_token(token: str) -> bool:
        """Returns True if a token looks like hallucination garbage."""
        clean = token.strip()
        if not clean:
            return True
        
        # Pure diacritical marks
        if all(c in _ARABIC_DIACRITICS or c in " " for c in clean):
            return True
        
        # Single extended Arabic chars that aren't real words
        if len(clean) <= 2 and any(c in _ARABIC_EXTENDED_CHARS for c in clean):
            return True
        
        # Single character followed by ی (common hallucination pattern: "ٸی", "ٵی")
        if len(clean) <= 3 and clean.endswith("ی") and len(clean) >= 2:
            base = clean[:-1]
            if all(c in _ARABIC_DIACRITICS or c in _ARABIC_EXTENDED_CHARS for c in base):
                return True

        # Very short token (1-2 chars) that's NOT a known legitimate short Urdu word
        if len(clean) <= 2:
            if clean in _LEGIT_SHORT_URDU:
                return False
            if clean.isdigit():
                return False
            if clean.isascii() and clean.isalpha():
                return False
            if len(clean) == 1:
                return True
        
        # Tokens that are just "ٹ" followed by 1-2 random chars (e.g. "ٹع", "ٹب", "ٹف")
        if len(clean) <= 3 and clean.startswith("ٹ") and clean not in {"ٹائم", "ٹائمز"}:
            return True
        
        return False

    # Sliding window: find where garbage starts
    WINDOW_SIZE = 10
    GARBAGE_THRESHOLD = 6  # If 6+ of 10 tokens are garbage, it's hallucination
    
    cutoff_index = len(tokens)
    
    for i in range(len(tokens) - WINDOW_SIZE + 1):
        window = tokens[i:i + WINDOW_SIZE]
        garbage_count = sum(1 for t in window if _is_garbage_token(t))
        
        if garbage_count >= GARBAGE_THRESHOLD:
            cutoff_index = i
            break
    
    if cutoff_index < len(tokens):
        clean_text = " ".join(tokens[:cutoff_index]).strip()
        removed_count = len(tokens) - cutoff_index
        try:
            print(f"[ShifaScribe AI] Hallucination detector: removed {removed_count} garbage tokens from position {cutoff_index}")
        except Exception:
            pass
        return clean_text
    
    return text


class WhisperTranscriber:
    def __init__(self, model_name: str = "openai/whisper-small"):
        self.model_name = model_name
        self.is_cuda_available = torch.cuda.is_available()
        
        if self.is_cuda_available:
            self.device_id = 0
            self.device_name = torch.cuda.get_device_name(0)
            self.device = f"cuda:0 ({self.device_name})"
            self.device_label = self.device
        else:
            self.device_id = -1
            self.device_name = "CPU"
            self.device = "cpu"
            self.device_label = "CPU Fallback"
        
        print(f"[ShifaScribe AI] Initializing Whisper model '{self.model_name}'...")
        print(f"[ShifaScribe AI] Acceleration Hardware: {self.device_label}")
        
        try:
            self.torch_dtype = torch.float16 if self.is_cuda_available else torch.float32
            dtype_label = "float16 (FP16 — half precision)" if self.is_cuda_available else "float32 (FP32 — CPU fallback)"
            print(f"[ShifaScribe AI] Precision Mode  : {dtype_label}")

            self.processor = WhisperProcessor.from_pretrained(self.model_name)
            self.model = WhisperForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=self.torch_dtype,
            )
            
            if self.is_cuda_available:
                self.model = self.model.to("cuda")
                
            self.model.eval()

            # Pre-compute the initial prompt token IDs for conditioning
            self._prompt_ids = self.processor.get_prompt_ids(WHISPER_INITIAL_PROMPT, return_tensors="pt")
            print(f"[ShifaScribe AI] Initial prompt loaded ({self._prompt_ids.shape[-1]} tokens)")

            print(f"[ShifaScribe AI] Whisper model '{self.model_name}' initialized successfully on {self.device_label}!")
        except Exception as e:
            print(f"[ShifaScribe AI] Error initializing Whisper model: {e}")
            raise e

    def transcribe_audio(self, file_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribes clinical audio dictation file.
        If language=None, auto-detects language for seamless code-switched (Urdu + English) recognition.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at path: {file_path}")

        print(f"[ShifaScribe AI] Running Whisper inference on: {file_path} (Language Mode: {language or 'Auto-Detect Code-Switched'})...")

        try:
            # Load raw audio array using librosa at 16kHz
            y, sr = librosa.load(file_path, sr=WHISPER_SAMPLE_RATE, mono=True)
            audio_duration = len(y) / sr
            print(f"[ShifaScribe AI] Audio loaded: {audio_duration:.2f}s, {len(y)} samples @ {sr}Hz")

            # ── CRITICAL FIX: Trim trailing silence to prevent hallucination ──
            # Whisper hallucinates when it encounters long silence (padded zeros).
            # We trim trailing silence BEFORE chunking to reduce phantom words.
            y = _trim_trailing_silence(y, sr)
            trimmed_duration = len(y) / sr
            if trimmed_duration < audio_duration - 0.5:
                print(f"[ShifaScribe AI] Trimmed trailing silence: {audio_duration:.2f}s → {trimmed_duration:.2f}s")
            audio_duration = trimmed_duration

            all_transcriptions = []

            # ── Build chunks WITHOUT wasteful zero-padding ────────────────
            # Previously: pad every chunk to 30s with zeros → Whisper hallucinates on the silence
            # Now: pass raw audio directly to the processor, which handles mel-spectrogram padding internally.
            # Only split into 30s chunks if audio is longer than 30s.
            if len(y) <= WHISPER_N_SAMPLES:
                chunks_to_process = [y]  # NO padding — pass raw audio
            else:
                stride = WHISPER_SAMPLE_RATE * 25  # 25-second stride (5s overlap)
                chunks_to_process = []
                for start in range(0, len(y), stride):
                    end = min(start + WHISPER_N_SAMPLES, len(y))
                    chunk = y[start:end]
                    # Only include chunks with at least 1 second of audio
                    if len(chunk) >= WHISPER_SAMPLE_RATE:
                        chunks_to_process.append(chunk)

            print(f"[ShifaScribe AI] Processing {len(chunks_to_process)} audio chunk(s)...")

            # Calculate max tokens based on audio duration
            # Rule of thumb: ~33 tokens per second of speech (generous upper bound)
            # This prevents Whisper from generating way more text than the audio could contain
            max_tokens_per_chunk = max(50, int(30 * 33))  # For a full 30s chunk

            for i, chunk in enumerate(chunks_to_process):
                # The processor handles mel-spectrogram padding internally
                # — no need to manually pad the raw audio to 30 seconds
                input_features = self.processor(
                    chunk,
                    sampling_rate=WHISPER_SAMPLE_RATE,
                    return_tensors="pt",
                    padding="longest",
                ).input_features

                if self.is_cuda_available:
                    input_features = input_features.to("cuda", dtype=torch.float16)
                else:
                    input_features = input_features.to(dtype=torch.float32)

                # Calculate max tokens proportional to this chunk's duration
                chunk_duration = len(chunk) / WHISPER_SAMPLE_RATE
                chunk_max_tokens = max(30, int(chunk_duration * 33))

                # Anti-hallucination decoding config
                gen_kwargs = {
                    "max_new_tokens": chunk_max_tokens,
                    "num_beams": 1,
                    "temperature": 0.0,
                    "no_repeat_ngram_size": 3,
                    "condition_on_prev_tokens": False,
                }

                # Initial prompt conditioning — guides Whisper to expect medical dictation
                try:
                    if self._prompt_ids is not None:
                        prompt = self._prompt_ids
                        if self.is_cuda_available:
                            prompt = prompt.to("cuda")
                        # Ensure prompt_ids is always a 1-d tensor regardless of get_prompt_ids return shape
                        gen_kwargs["prompt_ids"] = prompt.flatten()
                except Exception:
                    pass  # If prompt fails, proceed without it

                if language:
                    gen_kwargs["forced_decoder_ids"] = self.processor.get_decoder_prompt_ids(
                        language=language, task="transcribe"
                    )

                with torch.no_grad():
                    predicted_ids = self.model.generate(
                        input_features,
                        **gen_kwargs
                    )

                chunk_text = self.processor.batch_decode(
                    predicted_ids, skip_special_tokens=True
                )[0].strip()
                
                # Post-processing Phase 1: remove repeated-word hallucination loops
                chunk_text = _clean_hallucinated_repetitions(chunk_text)
                
                # Post-processing Phase 2: remove character-soup hallucination garbage
                chunk_text = _clean_character_soup_hallucination(chunk_text)
                
                if chunk_text:
                    all_transcriptions.append(chunk_text)
                    try:
                        print(f"[ShifaScribe AI] Chunk {i+1}/{len(chunks_to_process)}: '{chunk_text}'")
                    except Exception:
                        print(f"[ShifaScribe AI] Chunk {i+1}/{len(chunks_to_process)}: ({len(chunk_text)} chars)")

            transcribed_text = " ".join(all_transcriptions).strip()
            
            # Final pass: clean any cross-chunk artifacts
            transcribed_text = _clean_hallucinated_repetitions(transcribed_text)
            transcribed_text = _clean_character_soup_hallucination(transcribed_text)
            
            try:
                print(f"[ShifaScribe AI] Transcription complete. Final output: '{transcribed_text}' ({len(transcribed_text)} chars)")
            except Exception:
                print(f"[ShifaScribe AI] Transcription complete. Output length: {len(transcribed_text)} chars")
            
            return {
                "status": "success",
                "text": transcribed_text,
                "model": self.model_name,
                "language": language or "auto",
                "hardware": self.device_label,
                "audio_duration_sec": round(audio_duration, 2),
                "chunks_processed": len(chunks_to_process),
                "file_path": file_path,
            }
        except Exception as e:
            print(f"[ShifaScribe AI] Transcription failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "model": self.model_name,
                "hardware": self.device_label,
                "file_path": file_path,
            }


def _trim_trailing_silence(audio: np.ndarray, sr: int, 
                           top_db: int = 30, min_duration: float = 1.0) -> np.ndarray:
    """
    Trim trailing silence from audio to prevent Whisper from hallucinating
    on silent padding. Keeps at least min_duration seconds of audio.
    
    Uses librosa's effects.trim() which detects silence based on dB threshold.
    """
    try:
        # librosa.effects.trim returns (trimmed_audio, (start_index, end_index))
        trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        
        # Ensure we keep at least min_duration seconds
        min_samples = int(min_duration * sr)
        if len(trimmed) < min_samples:
            return audio[:max(min_samples, len(audio))]
        
        # Add a small buffer (0.3s) after the last detected sound
        buffer_samples = int(0.3 * sr)
        end_idx = min(len(trimmed) + buffer_samples, len(audio))
        return audio[:end_idx]
    except Exception:
        return audio  # If trimming fails, return original
