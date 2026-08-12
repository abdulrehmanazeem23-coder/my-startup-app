import os
import uuid
import shutil
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
from ai.audio_processor import sanitize_audio
from ai.whisper_service import WhisperTranscriber

# Auto-create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShifaScribe AI Medical Scribe API",
    description="FastAPI Backend, Audio Processing & Local Whisper AI Engine",
    version="0.2.0",
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
    Background Task Worker:
    1. Sanitizes raw audio input using Librosa (noise reduction & silence trimming).
    2. Runs Whisper AI speech-to-text inference.
    3. Updates task_store with the final transcribed text.
    """
    global task_store
    print(f"[ShifaScribe Worker] Background transcription task started for task_id: {task_id}")
    
    try:
        # Step 1: Sanitize raw audio input
        sanitized_filename = f"sanitized_{os.path.basename(raw_file_path)}"
        sanitized_file_path = os.path.join(STORAGE_DIR, sanitized_filename)
        
        sanitization_res = sanitize_audio(raw_file_path, sanitized_file_path, top_db=20)
        
        # Step 2: Run Whisper AI speech-to-text inference
        ai_engine = get_transcriber_instance()
        transcription_res = ai_engine.transcribe_audio(sanitized_file_path, language="ur")
        
        transcribed_text = transcription_res.get("text", "")
        
        # Step 3: Update task_store
        task_store[task_id] = {
            "status": "completed",
            "task_id": task_id,
            "consultation_id": consultation_id,
            "text": transcribed_text,
            "raw_file_path": raw_file_path,
            "sanitized_file_path": sanitized_file_path,
            "sanitization": sanitization_res,
            "transcription_metadata": transcription_res,
            "completed_at": datetime.now().isoformat(),
        }
        print(f"[ShifaScribe Worker] Task '{task_id}' completed successfully! Text length: {len(transcribed_text)}")
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
        "service": "ShifaScribe Audio & AI Engine",
        "version": "0.2.0",
        "ai_model": "openai/whisper-small",
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
            "message": "Audio file uploaded successfully. Asynchronous transcription started.",
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
