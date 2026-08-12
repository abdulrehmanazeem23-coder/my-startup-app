import os
import librosa
import soundfile as sf

def sanitize_audio(input_path: str, output_path: str, top_db: int = 20) -> dict:
    """
    Sanitizes raw audio input by trimming leading/trailing silence and ambient background room noise.
    
    :param input_path: Path to raw input audio file (.webm, .wav, .mp3)
    :param output_path: Path where sanitized audio file will be saved (.wav / .webm)
    :param top_db: The threshold (in decibels) below reference to consider as silence (default: 20dB)
    :return: Dictionary containing sanitization metrics and output metadata
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input audio file not found at: {input_path}")

    print(f"[ShifaScribe Audio Sanitizer] Loading audio file: {input_path}...")
    
    try:
        # Load audio file forcing 16kHz sample rate for Whisper AI optimal compliance
        y, sr = librosa.load(input_path, sr=16000)
        original_duration = len(y) / sr

        # Apply noise reduction & silence trimming
        y_trimmed, index = librosa.effects.trim(y, top_db=top_db)
        trimmed_duration = len(y_trimmed) / sr
        noise_reduced = original_duration - trimmed_duration

        # Ensure target directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write sanitized audio file back to disk
        sf.write(output_path, y_trimmed, sr)

        print(f"[ShifaScribe Audio Sanitizer] Sanitization complete!")
        print(f" - Original Duration: {original_duration:.2f} seconds")
        print(f" - Sanitized Duration: {trimmed_duration:.2f} seconds")
        print(f" - Noise/Silence Trimmed: {noise_reduced:.2f} seconds")
        print(f" - Saved to: {output_path}")

        return {
            "status": "success",
            "original_duration_sec": round(original_duration, 2),
            "trimmed_duration_sec": round(trimmed_duration, 2),
            "noise_reduced_sec": round(noise_reduced, 2),
            "sample_rate": sr,
            "top_db_threshold": top_db,
            "input_path": input_path,
            "output_path": output_path,
        }
    except Exception as e:
        print(f"[ShifaScribe Audio Sanitizer] Error sanitizing audio file: {e}")
        return {
            "status": "error",
            "message": str(e),
            "input_path": input_path,
            "output_path": output_path,
        }
