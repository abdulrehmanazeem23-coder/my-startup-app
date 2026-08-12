import os
import shutil
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShifaScribe AI Medical Scribe API",
    description="FastAPI Backend & Audio Storage Engine for ShifaScribe System",
    version="0.1.0",
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

# Workspace Audio Storage Directory
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage", "audio")
os.makedirs(STORAGE_DIR, exist_ok=True)

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
        "service": "ShifaScribe Audio Engine",
        "version": "0.1.0",
    }

# Day 5 Endpoint: Asynchronous Audio File Upload
@app.post("/api/consultation/upload-audio", status_code=status.HTTP_201_CREATED)
async def upload_consultation_audio(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None),
    doctor_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_ext = os.path.splitext(file.filename)[1] or ".webm"
        saved_filename = f"opd_consultation_{timestamp}{original_ext}"
        saved_file_path = os.path.join(STORAGE_DIR, saved_filename)

        # Asynchronously read file bytes
        contents = await file.read()
        file_size_bytes = len(contents)
        file_size_kb = round(file_size_bytes / 1024, 2)

        # Write audio file to local storage workspace
        with open(saved_file_path, "wb") as f:
            f.write(contents)

        # Save metadata to database consultation_logs table
        consultation_entry = models.ConsultationLog(
            patient_id=patient_id,
            doctor_id=doctor_id,
            audio_file_path=saved_file_path,
            file_size_kb=file_size_kb,
            mime_type=file.content_type or "audio/webm",
            status="uploaded",
        )
        db.add(consultation_entry)
        db.commit()
        db.refresh(consultation_entry)

        return {
            "status": "success",
            "message": "Audio file captured and stored successfully",
            "consultation_id": consultation_entry.id,
            "filename": saved_filename,
            "file_path": saved_file_path,
            "size_kb": file_size_kb,
            "mime_type": file.content_type or "audio/webm",
            "created_at": consultation_entry.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save audio file: {str(e)}",
        )
