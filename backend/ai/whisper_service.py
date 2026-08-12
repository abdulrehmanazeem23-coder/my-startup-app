import os

# Disable tqdm progress bars in background worker threads to prevent Windows stderr flush errors
os.environ["TQDM_DISABLE"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import torch
import librosa
import numpy as np
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Whisper processes audio in 30-second windows at 16kHz
WHISPER_SAMPLE_RATE = 16000
WHISPER_CHUNK_LENGTH = 30  # seconds
WHISPER_N_SAMPLES = WHISPER_SAMPLE_RATE * WHISPER_CHUNK_LENGTH  # 480,000 samples

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
            self.processor = WhisperProcessor.from_pretrained(self.model_name)
            self.model = WhisperForConditionalGeneration.from_pretrained(self.model_name)
            
            if self.is_cuda_available:
                self.model = self.model.to("cuda")
                
            self.model.eval()
            print(f"[ShifaScribe AI] Whisper model '{self.model_name}' initialized successfully on {self.device_label}!")
        except Exception as e:
            print(f"[ShifaScribe AI] Error initializing Whisper model: {e}")
            raise e

    def _pad_or_trim(self, audio: np.ndarray) -> np.ndarray:
        """
        Pad or trim audio to exactly 30 seconds (480,000 samples at 16kHz).
        Whisper was trained on 30-second log-mel spectrograms — short clips
        that aren't padded cause the model to 'repeat' or miss tokens.
        """
        if len(audio) > WHISPER_N_SAMPLES:
            # For longer audio, split and concatenate results outside this func
            audio = audio[:WHISPER_N_SAMPLES]
        else:
            # Zero-pad to 30 seconds
            pad_width = WHISPER_N_SAMPLES - len(audio)
            audio = np.pad(audio, (0, pad_width), mode="constant")
        return audio

    def transcribe_audio(self, file_path: str, language: str = "ur") -> dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at path: {file_path}")

        print(f"[ShifaScribe AI] Running Whisper inference on: {file_path} (Hardware: {self.device_label})...")

        try:
            # Load raw audio array using librosa at 16kHz
            y, sr = librosa.load(file_path, sr=WHISPER_SAMPLE_RATE, mono=True)
            audio_duration = len(y) / sr
            print(f"[ShifaScribe AI] Audio loaded: {audio_duration:.2f}s, {len(y)} samples @ {sr}Hz")

            all_transcriptions = []

            # Process in 30-second chunks for longer recordings
            if len(y) <= WHISPER_N_SAMPLES:
                # Short audio: pad to full 30-second window for best accuracy
                chunk = self._pad_or_trim(y)
                chunks_to_process = [chunk]
            else:
                # Long audio: split into overlapping 30-second windows
                stride = WHISPER_SAMPLE_RATE * 25  # 25-second stride (5s overlap)
                chunks_to_process = []
                for start in range(0, len(y), stride):
                    end = min(start + WHISPER_N_SAMPLES, len(y))
                    chunk = y[start:end]
                    chunk = self._pad_or_trim(chunk)
                    chunks_to_process.append(chunk)

            print(f"[ShifaScribe AI] Processing {len(chunks_to_process)} audio chunk(s)...")

            for i, chunk in enumerate(chunks_to_process):
                # Build log-mel spectrogram features (Whisper's native input format)
                input_features = self.processor(
                    chunk,
                    sampling_rate=WHISPER_SAMPLE_RATE,
                    return_tensors="pt"
                ).input_features

                if self.is_cuda_available:
                    input_features = input_features.to("cuda")

                # Force language & transcription task decoder tokens
                forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                    language=language, task="transcribe"
                )

                with torch.no_grad():
                    predicted_ids = self.model.generate(
                        input_features,
                        forced_decoder_ids=forced_decoder_ids,
                        # Generation quality settings
                        num_beams=5,               # Beam search for better accuracy
                        temperature=0.0,           # Greedy / deterministic decoding
                        condition_on_prev_tokens=False,
                        compression_ratio_threshold=2.4,
                        logprob_threshold=-1.0,
                        no_speech_threshold=0.6,
                    )

                chunk_text = self.processor.batch_decode(
                    predicted_ids, skip_special_tokens=True
                )[0].strip()
                
                if chunk_text:
                    all_transcriptions.append(chunk_text)
                    print(f"[ShifaScribe AI] Chunk {i+1}/{len(chunks_to_process)}: '{chunk_text}'")

            transcribed_text = " ".join(all_transcriptions).strip()
            print(f"[ShifaScribe AI] Transcription complete. Final output: '{transcribed_text}' ({len(transcribed_text)} chars)")
            
            return {
                "status": "success",
                "text": transcribed_text,
                "model": self.model_name,
                "language": language,
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
