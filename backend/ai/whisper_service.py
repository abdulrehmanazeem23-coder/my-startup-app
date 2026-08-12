import os

# Disable tqdm progress bars in background worker threads to prevent Windows stderr flush errors
os.environ["TQDM_DISABLE"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration, pipeline

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

    def transcribe_audio(self, file_path: str, language: str = "ur") -> dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found at path: {file_path}")

        print(f"[ShifaScribe AI] Running Whisper inference on: {file_path} (Hardware: {self.device_label})...")

        try:
            # Load raw audio array using librosa at 16kHz
            y, sr = librosa.load(file_path, sr=16000)

            # Process input audio features
            input_features = self.processor(y, sampling_rate=sr, return_tensors="pt").input_features
            
            if self.is_cuda_available:
                input_features = input_features.to("cuda")

            # Generate token IDs
            forced_decoder_ids = self.processor.get_decoder_prompt_ids(language=language, task="transcribe")
            
            with torch.no_grad():
                predicted_ids = self.model.generate(input_features, forced_decoder_ids=forced_decoder_ids)

            # Decode token IDs into raw text
            transcribed_text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
            
            print(f"[ShifaScribe AI] Transcription complete. Output text length: {len(transcribed_text)} characters.")
            
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
