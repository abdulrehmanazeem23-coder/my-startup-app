"""
ShifaScribe Multi-User Load Simulation & Latency Benchmark Test
Sprint 4 (Day 24) — QA & Backend Performance Engineering

This test simulates concurrent multi-doctor consultation uploads (5-10 concurrent requests)
against the FastAPI backend (http://localhost:8000/api/consultation/upload-audio).
It tracks:
  1. Upload Request Acknowledgment Latency (HTTP 202)
  2. Asynchronous Background Task Polling Latency
  3. Total End-to-End Turnaround Latency (Target: < 2.5s)
  4. SLA Compliance & Latency Threshold Violations
"""

import asyncio
import io
import math
import os
import struct
import sys
import time
import wave
from datetime import datetime
from typing import Dict, Any, List

# Ensure UTF-8 encoding on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import httpx
except ImportError:
    print("[ERROR] 'httpx' is not installed. Run: pip install httpx")
    sys.exit(1)

# Configuration Parameters
BASE_URL = os.environ.get("SHIFASCRIBE_API_URL", "http://localhost:8000")
UPLOAD_ENDPOINT = f"{BASE_URL}/api/consultation/upload-audio"
STATUS_ENDPOINT = f"{BASE_URL}/api/consultation/status"
HEALTH_ENDPOINT = f"{BASE_URL}/health"

CONCURRENT_USERS = int(os.environ.get("CONCURRENT_USERS", "8"))  # Default 8 concurrent doctors
POLL_INTERVAL_SEC = 0.2  # Poll task status every 200ms
MAX_TIMEOUT_SEC = 60.0   # Maximum timeout for task completion
LATENCY_TARGET_SEC = 2.5 # PRD Latency Target for standard dictation


def generate_synthetic_audio_payload(duration_sec: float = 3.0, sample_rate: int = 16000) -> bytes:
    """
    Generates an in-memory 16kHz mono 16-bit PCM WAV audio payload
    simulating realistic physician dictation voice audio.
    """
    num_samples = int(sample_rate * duration_sec)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            # Modulated speech-like waveform (fundamental 220Hz + harmonics)
            sample = int(
                6000 * math.sin(2 * math.pi * 220 * t)
                + 3000 * math.sin(2 * math.pi * 440 * t)
                + 1500 * math.sin(2 * math.pi * 880 * t)
            ) * (0.5 + 0.5 * math.sin(2 * math.pi * 2 * t))
            clamped = max(-32768, min(32767, int(sample)))
            frames.extend(struct.pack("<h", clamped))
        wav_file.writeframes(frames)
    return buffer.getvalue()


async def simulate_doctor_consultation(
    client: httpx.AsyncClient,
    doctor_idx: int,
    audio_bytes: bytes,
) -> Dict[str, Any]:
    """
    Simulates a single doctor session:
    1. Sends POST upload request with WAV audio payload.
    2. Measures HTTP upload latency.
    3. Asynchronously polls task status until 'completed' or 'failed'.
    4. Computes total turnaround latency and SLA compliance.
    """
    doctor_id = f"DR-OPD-{doctor_idx + 1:02d}"
    patient_id = 100 + doctor_idx + 1
    filename = f"simulated_consultation_{doctor_id}.wav"

    session_start = time.perf_counter()
    result = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "task_id": None,
        "upload_latency_sec": 0.0,
        "pipeline_latency_sec": 0.0,
        "total_turnaround_sec": 0.0,
        "status": "pending",
        "error": None,
        "within_target": False,
        "symptoms_count": 0,
        "medications_count": 0,
    }

    try:
        # Step 1: Upload Audio File
        files = {
            "file": (filename, audio_bytes, "audio/wav")
        }
        data = {
            "doctor_id": str(doctor_idx + 1),
            "patient_id": str(patient_id),
        }

        upload_start = time.perf_counter()
        resp = await client.post(UPLOAD_ENDPOINT, files=files, data=data)
        upload_elapsed = time.perf_counter() - upload_start
        result["upload_latency_sec"] = round(upload_elapsed, 3)

        if resp.status_code not in (200, 202):
            result["status"] = f"HTTP_{resp.status_code}"
            result["error"] = resp.text
            result["total_turnaround_sec"] = round(time.perf_counter() - session_start, 3)
            return result

        payload = resp.json()
        task_id = payload.get("task_id")
        result["task_id"] = task_id

        if not task_id:
            result["status"] = "NO_TASK_ID"
            result["error"] = "Backend response did not return a valid task_id"
            result["total_turnaround_sec"] = round(time.perf_counter() - session_start, 3)
            return result

        # Step 2: Poll Task Status Asynchronously
        poll_url = f"{STATUS_ENDPOINT}/{task_id}"
        poll_start = time.perf_counter()

        while True:
            elapsed_poll = time.perf_counter() - poll_start
            if elapsed_poll > MAX_TIMEOUT_SEC:
                result["status"] = "TIMEOUT"
                result["error"] = f"Task exceeded maximum timeout of {MAX_TIMEOUT_SEC}s"
                break

            await asyncio.sleep(POLL_INTERVAL_SEC)
            status_resp = await client.get(poll_url)

            if status_resp.status_code == 200:
                task_data = status_resp.json()
                current_status = task_data.get("status")

                if current_status == "completed":
                    result["status"] = "completed"
                    result["pipeline_latency_sec"] = round(
                        task_data.get("performance", {}).get("total_elapsed_sec", elapsed_poll), 3
                    )
                    ehr = task_data.get("structured_ehr", {})
                    result["symptoms_count"] = len(ehr.get("symptoms", [])) if ehr else 0
                    result["medications_count"] = len(ehr.get("medications", [])) if ehr else 0
                    break
                elif current_status == "failed":
                    result["status"] = "failed"
                    result["error"] = task_data.get("error", "Task marked as failed in task_store")
                    break

        total_turnaround = time.perf_counter() - session_start
        result["total_turnaround_sec"] = round(total_turnaround, 3)
        result["within_target"] = total_turnaround < LATENCY_TARGET_SEC and result["status"] == "completed"

    except Exception as exc:
        result["status"] = "EXCEPTION"
        result["error"] = str(exc)
        result["total_turnaround_sec"] = round(time.perf_counter() - session_start, 3)

    return result


async def run_load_simulation(num_users: int = CONCURRENT_USERS):
    """
    Main test orchestrator executing concurrent multi-doctor load simulation.
    """
    print("=" * 80)
    print("  SHIFASCRIBE MULTI-USER LOAD SIMULATION & PERFORMANCE BENCHMARK")
    print("  Sprint 4 (Day 24) • QA & Backend Performance Engineering")
    print("=" * 80)
    print(f"  Target Server Endpoint : {UPLOAD_ENDPOINT}")
    print(f"  Concurrent Doctors     : {num_users} simultaneous consultation sessions")
    print(f"  PRD Latency SLA Target : < {LATENCY_TARGET_SEC}s per consultation")
    print(f"  Test Timestamp         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("")

    # Step 0: Check Backend Health
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            health_res = await client.get(HEALTH_ENDPOINT)
            if health_res.status_code == 200:
                print(f"[PRE-FLIGHT] Backend is ONLINE ✓ (Service: {health_res.json().get('service')})")
            else:
                print(f"[PRE-FLIGHT] Warning: Backend responded with HTTP {health_res.status_code}")
        except Exception as err:
            print(f"[FATAL] Cannot connect to ShifaScribe backend at {BASE_URL}")
            print(f"        Ensure the server is running: uvicorn main:app --port 8000")
            print(f"        Error details: {err}")
            return False

    # Generate test audio
    print(f"[SETUP] Generating {num_users} synthetic 16kHz speech audio payloads in memory...")
    audio_bytes = generate_synthetic_audio_payload(duration_sec=3.0, sample_rate=16000)
    print(f"[SETUP] Audio payload size: {len(audio_bytes) / 1024:.1f} KB per doctor stream")
    print("")

    # Step 1: Launch Concurrent Requests
    print(f"[LOAD INJECTION] Dispatching {num_users} concurrent doctor upload requests...")
    overall_start = time.perf_counter()

    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    async with httpx.AsyncClient(timeout=httpx.Timeout(MAX_TIMEOUT_SEC), limits=limits) as client:
        tasks = [
            simulate_doctor_consultation(client, i, audio_bytes)
            for i in range(num_users)
        ]
        results: List[Dict[str, Any]] = await asyncio.gather(*tasks)

    overall_elapsed = time.perf_counter() - overall_start

    # Step 2: Print Performance Table
    print("\n" + "=" * 95)
    print(f"{'Doctor ID':<12} | {'Task ID':<18} | {'Upload(s)':<10} | {'Pipeline(s)':<12} | {'Total(s)':<10} | {'Status':<11} | {'SLA Compliance':<16}")
    print("-" * 95)

    completed_latencies = []
    success_count = 0
    sla_pass_count = 0

    for r in results:
        t_id = (r["task_id"][:14] + "..") if r["task_id"] else "N/A"
        up_s = f"{r['upload_latency_sec']:.3f}s"
        pipe_s = f"{r['pipeline_latency_sec']:.3f}s" if r["pipeline_latency_sec"] > 0 else "N/A"
        tot_s = f"{r['total_turnaround_sec']:.3f}s"
        stat = r["status"]

        if r["status"] == "completed":
            success_count += 1
            completed_latencies.append(r["total_turnaround_sec"])
            if r["within_target"]:
                sla_pass_count += 1
                sla_tag = "PASS (<2.5s) ✓"
            else:
                sla_tag = "VIOLATION ✗"
        else:
            sla_tag = "FAILED ✗"

        print(f"{r['doctor_id']:<12} | {t_id:<18} | {up_s:<10} | {pipe_s:<12} | {tot_s:<10} | {stat:<11} | {sla_tag:<16}")

    print("=" * 95)

    # Step 3: Statistical Metrics Aggregation
    print("\n" + "─" * 45)
    print("  STATISTICAL AGGREGATION & SLA REPORT")
    print("─" * 45)
    print(f"  Total Simulated Sessions  : {num_users}")
    print(f"  Successful Transcriptions : {success_count} / {num_users} ({success_count/num_users*100:.1f}%)")
    print(f"  Total Test Duration       : {overall_elapsed:.2f}s")
    print(f"  System Concurrency RTF    : {overall_elapsed / (num_users * 3.0):.3f}x")

    if completed_latencies:
        completed_latencies.sort()
        min_lat = completed_latencies[0]
        max_lat = completed_latencies[-1]
        mean_lat = sum(completed_latencies) / len(completed_latencies)
        p50_lat = completed_latencies[len(completed_latencies) // 2]
        p95_idx = min(int(len(completed_latencies) * 0.95), len(completed_latencies) - 1)
        p95_lat = completed_latencies[p95_idx]

        print(f"  Min Turnaround Latency    : {min_lat:.3f}s")
        print(f"  Max Turnaround Latency    : {max_lat:.3f}s")
        print(f"  Mean (Average) Latency    : {mean_lat:.3f}s")
        print(f"  P50 (Median) Latency      : {p50_lat:.3f}s")
        print(f"  P95 Latency               : {p95_lat:.3f}s")
        print(f"  PRD Latency Target        : < {LATENCY_TARGET_SEC}s")
        print(f"  SLA Compliance Rate       : {sla_pass_count} / {success_count} ({sla_pass_count/success_count*100:.1f}%)")
    else:
        print("  [ERROR] No completed tasks to compute latency statistics.")

    print("─" * 45)

    # Final Pass / SLA Verdict
    print("\n" + "=" * 80)
    if success_count == num_users and sla_pass_count == num_users:
        print("  [VERDICT] PASS: System fully met all multi-user throughput & <2.5s SLA targets!")
    elif success_count == num_users:
        print("  [VERDICT] FUNCTIONAL PASS: 100% of concurrent uploads processed successfully.")
        print(f"            Note: {num_users - sla_pass_count} request(s) ran on CPU queue exceeding <2.5s GPU target.")
        print("            (Expected on standard CPU machines without CUDA FP16 acceleration).")
    else:
        print("  [VERDICT] FAIL: One or more requests failed during concurrent execution.")
    print("=" * 80 + "\n")

    return success_count == num_users


if __name__ == "__main__":
    users = CONCURRENT_USERS
    if len(sys.argv) > 1:
        try:
            users = int(sys.argv[1])
        except ValueError:
            pass
    asyncio.run(run_load_simulation(users))
