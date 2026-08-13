import os
import uuid
import time
import shutil
import json
from datetime import datetime
from typing import Optional

# Force UTF-8 output on Windows so emoji in print() don't crash the worker thread
os.environ["PYTHONIOENCODING"] = "utf-8"

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db, SessionLocal
import models
from ai.audio_processor import sanitize_audio
from ai.whisper_service import WhisperTranscriber
from nlp.entity_extractor import extract_full_prescription

# Auto-create & migrate database tables
Base.metadata.create_all(bind=engine)

def ensure_db_columns():
    """Safety migration helper to ensure new columns exist in SQLite database."""
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("PRAGMA table_info(consultation_logs);")).fetchall()
            existing_cols = [row[1] for row in result]
            if "transcription_text" not in existing_cols:
                conn.execute(text("ALTER TABLE consultation_logs ADD COLUMN transcription_text TEXT;"))
                print("[ShifaScribe DB Migration] Added 'transcription_text' column to consultation_logs!")
            if "structured_ehr" not in existing_cols:
                conn.execute(text("ALTER TABLE consultation_logs ADD COLUMN structured_ehr TEXT;"))
                print("[ShifaScribe DB Migration] Added 'structured_ehr' column to consultation_logs!")
            conn.commit()
    except Exception as err:
        print(f"[ShifaScribe DB Migration Info] Column check: {err}")

ensure_db_columns()

app = FastAPI(
    title="ShifaScribe AI Medical Scribe API",
    description="FastAPI Backend, Audio Processing, Whisper AI Engine & NLP Entity Extractor",
    version="0.4.0",
)

# CORS Middleware configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Workspace Storage Directory
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage", "audio")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Global AI Engine Instance & In-Memory Task Store
transcriber: Optional[WhisperTranscriber] = None
task_store: dict = {}

def get_transcriber_instance() -> WhisperTranscriber:
    global transcriber
    if transcriber is None:
        print("[ShifaScribe AI] Loading WhisperTranscriber instance...")
        transcriber = WhisperTranscriber(model_name="openai/whisper-small")
    return transcriber

def process_transcription_task(task_id: str, raw_file_path: str, consultation_id: Optional[int] = None):
    """
    Background Task Worker (Day 12 — Latency Tracked & NLP Entity Extraction):
    1. Sanitizes raw audio input using Librosa (noise reduction & silence trimming).
    2. Runs Whisper AI speech-to-text inference (fp16 on GPU, float32 on CPU).
    3. Passes raw transcribed text through NLP entity_extractor for structured EHR JSON.
    4. Updates task_store and saves structured EHR JSON into consultation_logs database table.
    """
    global task_store
    print(f"[ShifaScribe Worker] Background transcription task started for task_id: {task_id}")

    try:
        # ── Step 1: Sanitize raw audio ─────────────────────────────────────
        base_name = os.path.splitext(os.path.basename(raw_file_path))[0]
        sanitized_file_path = os.path.join(STORAGE_DIR, f"sanitized_{base_name}.wav")

        start_time = time.time()

        sanitization_res = sanitize_audio(raw_file_path, sanitized_file_path, top_db=45)
        sanitization_elapsed = round(time.time() - start_time, 3)
        print(f"[PERF] Sanitization completed in {sanitization_elapsed:.3f}s")

        # Target audio path for Whisper AI (use sanitized WAV if available, else raw audio)
        target_audio_path = sanitized_file_path if os.path.exists(sanitized_file_path) else raw_file_path

        # ── Step 2: Run Whisper AI speech-to-text inference ────────────────
        inference_start = time.time()

        ai_engine = get_transcriber_instance()
        # language=None enables auto-detection for code-switched (Urdu + English) dictation
        transcription_res = ai_engine.transcribe_audio(target_audio_path, language=None)

        inference_elapsed = round(time.time() - inference_start, 3)
        print(f"[PERF] Whisper inference completed in {inference_elapsed:.3f}s")

        # ── Step 3: Calculate & log total pipeline latency ─────────────────
        total_elapsed = round(time.time() - start_time, 3)
        audio_duration = transcription_res.get("audio_duration_sec", 0)
        rtf = round(total_elapsed / audio_duration, 3) if audio_duration > 0 else None
        latency_ok = total_elapsed < 2.5
        latency_status = "[PASSED] WITHIN TARGET" if latency_ok else "[INFO] CPU BASELINE (GPU target: <2.5s)"

        print("")
        print(f"{'=' * 55}")
        print(f"[PERFORMANCE] Transcription pipeline completed in {total_elapsed:.2f}s")
        print(f"[PERFORMANCE]   Sanitization  : {sanitization_elapsed:.3f}s")
        print(f"[PERFORMANCE]   Whisper AI    : {inference_elapsed:.3f}s")
        print(f"[PERFORMANCE]   Audio Duration: {audio_duration:.2f}s")
        print(f"[PERFORMANCE]   RTF           : {rtf}x" if rtf else "[PERFORMANCE]   RTF           : N/A")
        print(f"[PERFORMANCE]   PRD Target    : < 2.5s  -->  {latency_status}")
        print(f"{'=' * 55}")
        print("")

        transcribed_text = transcription_res.get("text", "")

        # ── Step 4: Day 12 NLP Entity Extraction ───────────────────────────
        structured_ehr = extract_full_prescription(transcribed_text)
        print(f"[ShifaScribe NLP] Extracted Symptoms   : {structured_ehr.get('symptoms')}")
        print(f"[ShifaScribe NLP] Extracted Medications: {structured_ehr.get('medications')}")
        print(f"[ShifaScribe NLP] Dosage Frequency     : {structured_ehr.get('dosage_frequency')}")
        print(f"[ShifaScribe NLP] Duration             : {structured_ehr.get('duration')}")

        # ── Step 5: Update in-memory task_store ─────────────────────────────
        task_store[task_id] = {
            "status": "completed",
            "task_id": task_id,
            "consultation_id": consultation_id,
            "text": transcribed_text,
            "structured_ehr": structured_ehr,
            "raw_file_path": raw_file_path,
            "sanitized_file_path": target_audio_path,
            "sanitization": sanitization_res,
            "transcription_metadata": transcription_res,
            "performance": {
                "total_elapsed_sec": total_elapsed,
                "sanitization_elapsed_sec": sanitization_elapsed,
                "inference_elapsed_sec": inference_elapsed,
                "audio_duration_sec": audio_duration,
                "real_time_factor": rtf,
                "prd_target_sec": 2.5,
                "within_prd_target": total_elapsed < 2.5,
            },
            "completed_at": datetime.now().isoformat(),
        }

        # ── Step 6: Save structured EHR JSON to DB consultation_logs table ──
        if consultation_id:
            try:
                db = SessionLocal()
                consultation = db.query(models.ConsultationLog).filter(models.ConsultationLog.id == consultation_id).first()
                if consultation:
                    consultation.status = "completed"
                    consultation.transcription_text = transcribed_text
                    consultation.structured_ehr = json.dumps(structured_ehr)
                    db.commit()
                    print(f"[ShifaScribe DB] Updated ConsultationLog (id={consultation_id}) with transcription & structured EHR JSON!")
                db.close()
            except Exception as db_err:
                print(f"[ShifaScribe DB] Error saving to database log: {db_err}")

        print(f"[ShifaScribe Worker] Task '{task_id}' completed successfully!")
    except Exception as e:
        print(f"[ShifaScribe Worker] Task '{task_id}' failed: {e}")
        task_store[task_id] = {
            "status": "failed",
            "task_id": task_id,
            "consultation_id": consultation_id,
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to ShifaScribe AI Medical Scribe API",
        "docs": "http://localhost:8000/docs",
        "status": "online",
    }

@app.get("/health")
def health_check():
    return {
        "status": "API is running",
        "service": "ShifaScribe Audio, AI Engine & NLP Extractor",
        "version": "0.4.0",
        "ai_model": "openai/whisper-small",
        "nlp_engine": "ShifaScribe RegEx & Entity Extractor (Day 12)",
    }

# Day 8 Endpoint: Asynchronous Audio Upload with Background Whisper Task
@app.post("/api/consultation/upload-audio", status_code=status.HTTP_202_ACCEPTED)
async def upload_consultation_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None),
    doctor_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        # Generate unique task_id and timestamped filename
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_ext = os.path.splitext(file.filename)[1] or ".webm"
        saved_filename = f"opd_consultation_{timestamp}{original_ext}"
        saved_file_path = os.path.join(STORAGE_DIR, saved_filename)

        # Write audio bytes to disk
        contents = await file.read()
        file_size_kb = round(len(contents) / 1024, 2)
        with open(saved_file_path, "wb") as f:
            f.write(contents)

        # Save record to database
        consultation_entry = models.ConsultationLog(
            patient_id=patient_id,
            doctor_id=doctor_id,
            audio_file_path=saved_file_path,
            file_size_kb=file_size_kb,
            mime_type=file.content_type or "audio/webm",
            status="processing",
        )
        db.add(consultation_entry)
        db.commit()
        db.refresh(consultation_entry)

        # Register task status in task_store
        task_store[task_id] = {
            "status": "processing",
            "task_id": task_id,
            "consultation_id": consultation_entry.id,
            "filename": saved_filename,
            "size_kb": file_size_kb,
            "created_at": datetime.now().isoformat(),
        }

        # Enqueue background transcription task
        background_tasks.add_task(
            process_transcription_task,
            task_id=task_id,
            raw_file_path=saved_file_path,
            consultation_id=consultation_entry.id,
        )

        return {
            "status": "processing",
            "message": "Audio file uploaded successfully. Asynchronous transcription & NLP extraction started.",
            "task_id": task_id,
            "consultation_id": consultation_entry.id,
            "filename": saved_filename,
            "size_kb": file_size_kb,
            "status_url": f"/api/consultation/status/{task_id}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process audio upload: {str(e)}",
        )

# Day 8 Endpoint: Polling Endpoint for Transcription Task Status
@app.get("/api/consultation/status/{task_id}")
def get_transcription_status(task_id: str):
    if task_id not in task_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription task ID '{task_id}' not found.",
        )
    return task_store[task_id]
