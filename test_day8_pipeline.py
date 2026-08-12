import os
import sys
import time
import requests

# Set UTF-8 output encoding for Windows PowerShell console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

url_upload = "http://localhost:8000/api/consultation/upload-audio"
url_status = "http://localhost:8000/api/consultation/status/"

sample_file = r"c:\Users\Sys\Desktop\my-startup-app\backend\storage\audio\sanitized_test_audio.wav"

if not os.path.exists(sample_file):
    print("Creating sample test audio file...")
    os.makedirs(os.path.dirname(sample_file), exist_ok=True)
    with open(sample_file, "wb") as f:
        f.write(b"RIFF....WAVEfmt ....data....")

print("1. Sending POST /api/consultation/upload-audio request...")
with open(sample_file, "rb") as f:
    files = {"file": ("opd_sample.wav", f, "audio/wav")}
    data = {"patient_id": "104", "doctor_id": "4"}
    res = requests.post(url_upload, files=files, data=data)

print("Upload Response Status Code:", res.status_code)
upload_json = res.json()
print("Upload Response Payload:", upload_json)

task_id = upload_json.get("task_id")
print("\n2. Extracted Task ID:", task_id)

print("\n3. Polling GET /api/consultation/status/{task_id}...")
for i in range(15):
    time.sleep(1)
    status_res = requests.get(url_status + task_id)
    status_json = status_res.json()
    current_status = status_json.get("status")
    print(f"Poll #{i+1}: Status = {current_status}")
    
    if current_status in ["completed", "failed"]:
        print("\n==================================================")
        print("Final Task Result:")
        print("Status     :", current_status)
        print("Text Output:", status_json.get("text").encode('utf-8', errors='ignore').decode('utf-8'))
        print("Task ID    :", status_json.get("task_id"))
        print("Sanitizer  :", status_json.get("sanitization"))
        print("==================================================")
        break
