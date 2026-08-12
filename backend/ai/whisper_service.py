import os
import torch
from transformers import pipeline

class WhisperTranscriber:
    def __init__(self, model_name: str = "openai/whisper-small"):
        self.model_name = model_name
        self.is_cuda_available = torch.cuda.is_available()
        
        # Configure CUDA GPU device or CPU fallback
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
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=self.device_id,
                chunk_length_s=30,
            )
            print(f"[ShifaScribe AI] Whisper model '{self.model_name}' initialized successfully on {self.device_label}!")
        except Exception as e:
            print(f"[ShifaScribe AI] Error initializing Whisper pipeline: {e}")
            raise e

    def transcribe_audio(self, file_path: str, language: str = "ur") -> dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at path: {file_path}")

        print(f"[ShifaScribe AI] Running Whisper inference on: {file_path} (Hardware: {self.device_label})...")

        try:
            generate_kwargs = {"task": "transcribe"}
            if language:
                generate_kwargs["language"] = language

            result = self.pipe(
                file_path,
                generate_kwargs=generate_kwargs
            )

            transcribed_text = result.get("text", "").strip()
            print(f"[ShifaScribe AI] Transcription complete. Output length: {len(transcribed_text)} characters.")
            
            return {
                "status": "success",
                "text": transcribed_text,
                "model": self.model_name,
                "language": language,
                "hardware": self.device_label,
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
