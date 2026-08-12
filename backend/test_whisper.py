import os
import sys

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(__file__))

from ai.whisper_service import WhisperTranscriber

def test_whisper_initialization():
    print("==================================================")
    print("ShifaScribe Day 6 - Local Whisper AI Initialization")
    print("==================================================")
    print("Starting Whisper model download & pipeline cache...")
    
    try:
        transcriber = WhisperTranscriber(model_name="openai/whisper-small")
        print("\n[SUCCESS] OpenAI Whisper-Small model loaded successfully!")
        print(f"Model: {transcriber.model_name}")
        print(f"Device Target: {transcriber.device}")
        print("Model weights cached in Hugging Face local directory (~/.cache/huggingface/hub).")
        print("==================================================")
    except Exception as e:
        print(f"\n[ERROR] Failed to load Whisper model: {e}")

if __name__ == "__main__":
    test_whisper_initialization()
