import os
import torch
from transformers import pipeline

class WhisperTranscriber:
    def __init__(self, model_name: str = "openai/whisper-small"):
        self.model_name = model_name
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        print(f"[ShifaScribe AI] Initializing Whisper model '{self.model_name}' on device '{self.device}'...")
        
        try:
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=self.device,
                chunk_length_s=30,
            )
            print(f"[ShifaScribe AI] Whisper model '{self.model_name}' loaded successfully!")
        except Exception as e:
            print(f"[ShifaScribe AI] Error initializing Whisper pipeline: {e}")
            raise e

    def transcribe_audio(self, file_path: str, language: str = "ur") -> dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at path: {file_path}")

        print(f"[ShifaScribe AI] Running Whisper inference on file: {file_path}...")

        try:
            # Run automatic speech recognition inference
            result = self.pipe(
                file_path,
                generate_kwargs={"task": "transcribe", "language": language} if language else {"task": "transcribe"}
            )

            transcribed_text = result.get("text", "").strip()
            print(f"[ShifaScribe AI] Transcription complete. Generated text length: {len(transcribed_text)} characters.")
            
            return {
                "status": "success",
                "text": transcribed_text,
                "model": self.model_name,
                "language": language,
                "file_path": file_path,
            }
        except Exception as e:
            print(f"[ShifaScribe AI] Transcription failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "model": self.model_name,
                "file_path": file_path,
            }
