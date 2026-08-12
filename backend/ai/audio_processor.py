import os
import subprocess
import librosa
import soundfile as sf

def convert_to_wav_16k(input_path: str, target_wav_path: str):
    """
    Converts any input audio format (.webm, .m4a, .mp3, .ogg) into a clean 16kHz mono WAV file.
    Uses imageio-ffmpeg if available, falling back to system ffmpeg binary.
    """
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg_exe = "ffmpeg"

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        target_wav_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr.decode('utf-8', errors='ignore')}")

def sanitize_audio(input_path: str, output_path: str, top_db: int = 20) -> dict:
    """
    Sanitizes raw audio input by trimming leading/trailing silence and ambient background room noise.
    Handles WebM browser streams by converting to 16kHz WAV format first.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input audio file not found at: {input_path}")

    print(f"[ShifaScribe Audio Sanitizer] Processing audio file: {input_path}...")
    
    try:
        # Step 1: Ensure output file path uses .wav extension
        if not output_path.endswith(".wav"):
            output_path = os.path.splitext(output_path)[0] + ".wav"

        # Step 2: Convert input format (.webm, .mp3, etc.) to a temporary 16kHz WAV file if needed
        converted_temp_wav = os.path.splitext(input_path)[0] + "_temp16k.wav"
        
        try:
            convert_to_wav_16k(input_path, converted_temp_wav)
            load_source = converted_temp_wav
        except Exception as conv_err:
            print(f"[ShifaScribe Audio Sanitizer] Direct conversion warning: {conv_err}. Retrying librosa direct load...")
            load_source = input_path

        # Step 3: Load 16kHz audio array with librosa
        y, sr = librosa.load(load_source, sr=16000)
        original_duration = len(y) / sr

        # Step 4: Apply silence & background room noise trimming
        y_trimmed, index = librosa.effects.trim(y, top_db=top_db)
        trimmed_duration = len(y_trimmed) / sr
        noise_reduced = original_duration - trimmed_duration

        # Ensure target directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Step 5: Write sanitized 16kHz WAV file back to disk
        sf.write(output_path, y_trimmed, sr, format="WAV", subtype="PCM_16")

        # Cleanup temporary converted wav file
        if os.path.exists(converted_temp_wav) and converted_temp_wav != input_path:
            try:
                os.remove(converted_temp_wav)
            except Exception:
                pass

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
