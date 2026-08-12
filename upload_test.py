import requests

url = "http://localhost:8000/api/consultation/upload-audio"
file_path = r"c:\Users\Sys\Desktop\my-startup-app\backend\storage\audio\sample_test_consultation.webm"

with open(file_path, "rb") as f:
    files = {"file": ("opd_audio_test.webm", f, "audio/webm")}
    data = {"patient_id": "104", "doctor_id": "4"}
    response = requests.post(url, files=files, data=data)

print("Status Code:", response.status_code)
print("Response Payload:", response.json())
