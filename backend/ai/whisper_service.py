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
_ARABIC_DIACRITICS = set("ًٌٍَُِّْٰٕٖٓٔٗ٘ٙٚ")
_ARABIC_EXTENDED_CHARS = set("ٮٯٱٲٳٴٵٶٷٸٹٺٻټٽٿ")

# Common 1-2 char Urdu/Arabic words that are LEGITIMATE (don't flag these as gibberish)
_LEGIT_SHORT_URDU = {
    "کو", "ہے", "اور", "بھی", "اس", "کا", "کی", "کے", "نے", "سے", "پر",
    "تو", "جو", "یہ", "وہ", "ان", "اب", "جب", "تب", "نہ", "ہی", "میں",
    "ہم", "ہو", "دو", "یا", "آج", "کم", "بن", "آپ", "گی", "دن",
}


def _clean_hallucinated_repetitions(text: str) -> str:
    """
    Detects and removes Whisper hallucination loops where the same word or short
    phrase is repeated many times consecutively (e.g. "علمہ علمہ علمہ علمہ ...").
    
    Strategy:
    1. If any single token appears 5+ times consecutively, collapse to 1 occurrence.
    2. If any 2-3 word phrase repeats 4+ times consecutively, collapse to 1 occurrence.
    3. Remove leading/trailing whitespace artifacts.
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
    outputs random isolated characters, diacritics, and nonsense tokens instead
    of coherent speech.
    
    This is a DIFFERENT hallucination pattern from word-repetition:
    - Word repetition: "علمہ علمہ علمہ علمہ علمہ"
    - Character soup:  "ٸڈی ای ١ی ٨ی ٰی ٧ی ٵی ٱی ٲی ٴی ٿی ..."
    
    Detection strategy:
    Uses a sliding window of 12 tokens. If >= 8 tokens in the window are
    'garbage' (isolated diacritics, single extended chars, or very short
    non-meaningful tokens), we truncate the text at that point.
    """
    if not text:
        return text

    tokens = text.split()
    if len(tokens) < 15:
        return text  # Too short to contain meaningful + garbage sections

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
            # If base is a diacritic or extended char, it's garbage
            if all(c in _ARABIC_DIACRITICS or c in _ARABIC_EXTENDED_CHARS for c in base):
                return True

        # Very short token (1-2 chars) that's NOT a known legitimate short Urdu word
        # and NOT a number and NOT a common English word
        if len(clean) <= 2:
            if clean in _LEGIT_SHORT_URDU:
                return False
            if clean.isdigit():
                return False
            if clean.isascii() and clean.isalpha():
                return False  # English short words like "is", "to", etc.
            # Single isolated Urdu chars that aren't meaningful words
            if len(clean) == 1:
                return True
        
        # Tokens that are just "ٹ" followed by 1-2 random chars (e.g. "ٹع", "ٹب", "ٹف")
        if len(clean) <= 3 and clean.startswith("ٹ") and clean not in {"ٹائم", "ٹائمز"}:
            return True
        
        return False

    # Sliding window: find where garbage starts
    WINDOW_SIZE = 12
    GARBAGE_THRESHOLD = 8  # If 8+ of 12 tokens are garbage, it's hallucination
    
    cutoff_index = len(tokens)  # Default: keep everything
    
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
            print(f"[ShifaScribe AI] Whisper model '{self.model_name}' initialized successfully on {self.device_label}!")
        except Exception as e:
            print(f"[ShifaScribe AI] Error initializing Whisper model: {e}")
            raise e

    def _pad_or_trim(self, audio: np.ndarray) -> np.ndarray:
        """Pad or trim audio array to exactly 30 seconds (480,000 samples at 16kHz)."""
        if len(audio) > WHISPER_N_SAMPLES:
            audio = audio[:WHISPER_N_SAMPLES]
        else:
            pad_width = WHISPER_N_SAMPLES - len(audio)
            audio = np.pad(audio, (0, pad_width), mode="constant")
        return audio

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

            all_transcriptions = []

            # Process in 30-second chunks for longer recordings
            if len(y) <= WHISPER_N_SAMPLES:
                chunk = self._pad_or_trim(y)
                chunks_to_process = [chunk]
            else:
                stride = WHISPER_SAMPLE_RATE * 25  # 25-second stride (5s overlap)
                chunks_to_process = []
                for start in range(0, len(y), stride):
                    end = min(start + WHISPER_N_SAMPLES, len(y))
                    chunk = y[start:end]
                    chunk = self._pad_or_trim(chunk)
                    chunks_to_process.append(chunk)

            print(f"[ShifaScribe AI] Processing {len(chunks_to_process)} audio chunk(s)...")

            for i, chunk in enumerate(chunks_to_process):
                input_features = self.processor(
                    chunk,
                    sampling_rate=WHISPER_SAMPLE_RATE,
                    return_tensors="pt"
                ).input_features

                if self.is_cuda_available:
                    input_features = input_features.to("cuda", dtype=torch.float16)
                else:
                    input_features = input_features.to(dtype=torch.float32)

                # Anti-hallucination decoding config:
                # - no_repeat_ngram_size=3: prevents any 3-word phrase from repeating
                # - condition_on_prev=False: prevents hallucination cascading between chunks
                # - num_beams=1: greedy decoding for speed
                # - temperature=0.0: deterministic output
                gen_kwargs = {
                    "num_beams": 1,
                    "temperature": 0.0,
                    "no_repeat_ngram_size": 3,
                    "condition_on_prev_tokens": False,
                }

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
