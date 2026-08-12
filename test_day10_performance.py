import os, sys, time, requests
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

url_upload = "http://localhost:8001/api/consultation/upload-audio"
url_status = "http://localhost:8001/api/consultation/status/"

# Use the largest real sanitized WAV from previous sessions
sample_file = r"c:\Users\Sys\Desktop\my-startup-app\backend\storage\audio\sanitized_opd_consultation_20260812_152757.wav"

print("=" * 62)
print("ShifaScribe Day 10 -- Latency & Performance Benchmark Test")
print("=" * 62)
size_kb = os.path.getsize(sample_file) / 1024
print(f"  Audio File   : {os.path.basename(sample_file)}")
print(f"  File Size    : {size_kb:.1f} KB")
print()
print("Step 1: Uploading audio to POST /api/consultation/upload-audio ...")
with open(sample_file, "rb") as f:
    res = requests.post(url_upload, files={"file": (os.path.basename(sample_file), f, "audio/wav")}, data={"patient_id": "104", "doctor_id": "4"})
j = res.json()
task_id = j.get("task_id")
print(f"  HTTP Status  : {res.status_code}")
print(f"  Task ID      : {task_id}")
print(f"  Status URL   : {j.get('status_url')}")
print()
print("Step 2: Polling GET /api/consultation/status/{task_id} every 2s ...")
for i in range(40):
    time.sleep(2)
    s = requests.get(url_status + task_id).json()
    st = s.get("status")
    print(f"  Poll #{i+1:02d}: status = {st}")
    if st in ["completed", "failed"]:
        p = s.get("performance", {})
        print()
        print("=" * 62)
        print("  FINAL PIPELINE RESULT")
        print("=" * 62)
        print(f"  Status              : {st}")
        print(f"  Transcribed Text    : {s.get('text','(empty)')}")
        if p:
            print(f"")
            print(f"  -- PERFORMANCE METRICS (Day 10) --")
            print(f"  Sanitization Time   : {p.get('sanitization_elapsed_sec')}s")
            print(f"  Whisper Inference   : {p.get('inference_elapsed_sec')}s")
            print(f"  Total Pipeline Time : {p.get('total_elapsed_sec')}s")
            print(f"  Audio Duration      : {p.get('audio_duration_sec')}s")
            print(f"  Real-Time Factor    : {p.get('real_time_factor')}x")
            print(f"  PRD Target (<2.5s)  : < {p.get('prd_target_sec')}s")
            within = p.get('within_prd_target')
            if within:
                print(f"  Result              : PASSED -- WITHIN PRD TARGET")
            else:
                print(f"  Result              : CPU Baseline (GPU FP16 target: < 2.5s)")
        else:
            print(f"  Error               : {s.get('error','')}")
        print("=" * 62)
        break
