import os
import requests

# Test audio file generation
storage_dir = r"c:\Users\Sys\Desktop\my-startup-app\backend\storage\audio"
os.makedirs(storage_dir, exist_ok=True)

test_file_path = os.path.join(storage_dir, "sample_test_consultation.webm")
with open(test_file_path, "wb") as f:
    f.write(b"RIFF....WEBM-AUDIO-OPUS-SAMPLE-STREAM-DATA-SHIFASCRIBE-DAY5")

print("Created sample audio file for testing:", test_file_path)
