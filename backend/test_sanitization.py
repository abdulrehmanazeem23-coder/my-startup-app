import os
import sys
import numpy as np
import soundfile as sf

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(__file__))

from ai.audio_processor import sanitize_audio

def run_sanitization_test():
    print("==================================================")
    print("ShifaScribe Day 7 - Librosa Audio Sanitization Test")
    print("==================================================")
    
    storage_dir = os.path.join(os.path.dirname(__file__), "storage", "audio")
    os.makedirs(storage_dir, exist_ok=True)
    
    input_wav = os.path.join(storage_dir, "raw_test_audio.wav")
    output_wav = os.path.join(storage_dir, "sanitized_test_audio.wav")
    
    # Generate 5 seconds of sample audio (2s silence + 1s tone + 2s silence)
    sr = 16000
    t = np.linspace(0, 1.0, sr)
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
    silence = np.zeros(sr * 2)               # 2 seconds silence
    
    raw_signal = np.concatenate([silence, tone, silence])
    sf.write(input_wav, raw_signal, sr)
    
    print(f"Created dummy raw audio file: {input_wav}")
    print("Running Librosa noise/silence sanitization pipeline...")
    
    results = sanitize_audio(input_wav, output_wav, top_db=20)
    
    if results.get("status") == "success":
        print("\n[SUCCESS] Audio Sanitization Test Passed!")
        print(f"Original Duration : {results['original_duration_sec']}s")
        print(f"Sanitized Duration: {results['trimmed_duration_sec']}s")
        print(f"Silence Trimmed   : {results['noise_reduced_sec']}s")
        print(f"Cleaned File Saved: {results['output_path']}")
    else:
        print(f"\n[ERROR] Sanitization Failed: {results.get('message')}")
    print("==================================================")

if __name__ == "__main__":
    run_sanitization_test()
