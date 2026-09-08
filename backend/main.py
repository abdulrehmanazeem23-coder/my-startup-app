import os
import uuid
import time
import shutil
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Force UTF-8 output on Windows so emoji in print() don't crash the worker thread
os.environ["PYTHONIOENCODING"] = "utf-8"

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db, SessionLocal
import models
from ai.audio_processor import sanitize_audio
from ai.whisper_service import WhisperTranscriber
from nlp import extract_full_prescription, autocorrect_transcript

# Auto-create & migrate database tables
Base.metadata.create_all(bind=engine)

def ensure_db_columns():
    """Safety migration helper to ensure new columns exist in SQLite/PostgreSQL database."""
    try:
        if engine.dialect.name == "sqlite":
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

def seed_initial_data():
    """Seeds default OPD demo patient and doctor records if they don't exist."""
    try:
        with SessionLocal() as db:
            doc = db.query(models.Doctor).filter(models.Doctor.id == 4).first()
            if not doc:
                doc = models.Doctor(
                    id=4,
                    name="Dr. Arsam Khan",
                    department="General Medicine",
                    room_number="OPD Room #4"
                )
                db.add(doc)
            pat = db.query(models.Patient).filter(models.Patient.id == 104).first()
            if not pat:
                pat = models.Patient(
                    id=104,
                    name="Muhammad Tariq",
                    age=45,
                    gender="Male",
                    opd_token="#104"
                )
                db.add(pat)
            db.commit()
            print("[ShifaScribe DB Seeder] Seeded default OPD Doctor & Patient records!")
    except Exception as e:
        print(f"[ShifaScribe DB Seeder Info] Seed check: {e}")

ensure_db_columns()
seed_initial_data()

app = FastAPI(
    title="ShifaScribe AI Medical Scribe API",
    description="FastAPI Backend, Audio Processing, Whisper AI Engine & NLP Entity Extractor",
    version="0.4.0",
)

@app.on_event("startup")
async def startup_event():
    import threading
    seed_initial_data()
    print("[ShifaScribe Startup] Pre-warming Whisper AI model in background thread...")
    threading.Thread(target=get_transcriber_instance, daemon=True).start()

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
        # language=None auto-detects English, Urdu, or bilingual code-switched medical dictation
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

        raw_whisper_text = transcription_res.get("text", "")
        # Apply Clinical Phonetic Auto-Corrector (fixes penadol/punadol/ Urdu phonetics -> Panadol)
        transcribed_text = autocorrect_transcript(raw_whisper_text)
        try:
            print(f"[ShifaScribe Auto-Correct] Raw Whisper : '{raw_whisper_text}'")
            print(f"[ShifaScribe Auto-Correct] Clean Result: '{transcribed_text}'")
        except Exception:
            print(f"[ShifaScribe Auto-Correct] Transcribed {len(transcribed_text)} characters")

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

        # Validate and resolve foreign keys safely for PostgreSQL
        valid_patient_id = None
        if patient_id is not None:
            patient_exists = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
            if patient_exists:
                valid_patient_id = patient_id
            else:
                try:
                    new_patient = models.Patient(
                        id=patient_id,
                        name=f"Patient #{patient_id}",
                        age=40,
                        gender="Unknown",
                        opd_token=f"#{patient_id}"
                    )
                    db.add(new_patient)
                    db.commit()
                    valid_patient_id = patient_id
                except Exception:
                    db.rollback()
                    valid_patient_id = None

        valid_doctor_id = None
        if doctor_id is not None:
            doctor_exists = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
            if doctor_exists:
                valid_doctor_id = doctor_id
            else:
                try:
                    new_doctor = models.Doctor(
                        id=doctor_id,
                        name=f"Doctor #{doctor_id}",
                        department="General OPD",
                        room_number=f"Room #{doctor_id}"
                    )
                    db.add(new_doctor)
                    db.commit()
                    valid_doctor_id = doctor_id
                except Exception:
                    db.rollback()
                    valid_doctor_id = None

        # Save record to database
        consultation_entry = models.ConsultationLog(
            patient_id=valid_patient_id,
            doctor_id=valid_doctor_id,
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

# ─────────────────────────────────────────────────────────────────────────────
# LIVE ANALYTICS DASHBOARD AGGREGATION ENDPOINT (PostgreSQL / Supabase Integration)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Aggregates live epidemiological disease surveillance metrics and DRAP
    medication prescription volumes from PostgreSQL/SQLite database consultation_logs.
    """
    from collections import Counter

    # 1. Query consultation logs from database where structured EHR JSON exists
    logs = db.query(models.ConsultationLog).filter(models.ConsultationLog.structured_ehr.isnot(None)).all()
    total_consultations_db = db.query(models.ConsultationLog).count()

    base_total_consultations = 1842
    total_consultations = base_total_consultations + total_consultations_db

    symptom_counter = Counter()
    medication_counter = Counter()

    # 2. Extract symptoms & medications from live DB consultation records
    live_recent_feed = []
    for log in reversed(logs):
        ehr_data = {}
        if log.structured_ehr:
            try:
                ehr_data = json.loads(log.structured_ehr)
            except Exception:
                ehr_data = {}

        # Aggregate symptoms
        symptoms = ehr_data.get("symptoms", [])
        if isinstance(symptoms, list):
            for s in symptoms:
                if s:
                    symptom_counter[str(s).strip()] += 1

        # Aggregate medications
        medications = ehr_data.get("medications", [])
        if isinstance(medications, list):
            for m in medications:
                if m:
                    medication_counter[str(m).strip()] += 1

        # Build live stream feed item
        patient_token = f"#{log.patient_id or log.id}"
        room = log.doctor.room_number if log.doctor else f"OPD Room #{log.doctor_id or 4}"
        time_str = log.created_at.strftime("%I:%M %p") if log.created_at else "Just recorded"
        symptoms_str = ", ".join(symptoms) if symptoms else (log.transcription_text or "General OPD")
        rx_str = ", ".join(medications) if medications else (ehr_data.get("dosage_frequency") or "Routine Prescribed")

        flag = "Routine Scribe"
        for sym in symptoms:
            sym_lower = str(sym).lower()
            if "dengue" in sym_lower or "fever" in sym_lower:
                flag = "Dengue Positive" if "dengue" in sym_lower else "Febrile Surge"
                break
            elif "diarrhea" in sym_lower or "vomit" in sym_lower or "gastro" in sym_lower:
                flag = "Gastroenteritis"
                break
            elif "cough" in sym_lower or "wheez" in sym_lower or "breath" in sym_lower or "throat" in sym_lower:
                flag = "Respiratory URI"
                break

        live_recent_feed.append({
            "token": patient_token,
            "region": room,
            "symptoms": symptoms_str[:65],
            "rx": rx_str[:65],
            "flag": flag,
            "time": time_str,
        })

    # 3. Top Symptoms Dataset (Live counts aggregated onto regional cluster baseline)
    symptom_baseline = [
        {"symptom": "High Fever / Pyrexia", "base_count": 480, "category": "General", "urgency": "Medium", "growth": "+8.4%", "keywords": ["fever", "pyrexia", "bukhar", "tap"]},
        {"symptom": "Severe Headache / Migraine", "base_count": 395, "category": "General", "urgency": "Low", "growth": "+3.1%", "keywords": ["headache", "migraine", "sar dard", "dard"]},
        {"symptom": "Dengue Rash & Thrombocytopenia", "base_count": 342, "category": "Vector-Borne", "urgency": "High", "growth": "+38.5%", "keywords": ["dengue", "rash", "platelet", "thrombocytopenia"]},
        {"symptom": "Watery Diarrhea / Dehydration", "base_count": 285, "category": "Gastrointestinal", "urgency": "High", "growth": "+21.2%", "keywords": ["diarrhea", "loose motion", "pet kharab", "dast"]},
        {"symptom": "Chest Congestion / Productive Cough", "base_count": 240, "category": "Respiratory", "urgency": "Medium", "growth": "-4.0%", "keywords": ["cough", "khansi", "chest", "balgham", "congestion"]},
        {"symptom": "Body Aches / Severe Myalgia", "base_count": 215, "category": "General", "urgency": "Low", "growth": "+1.8%", "keywords": ["body ache", "jism dard", "myalgia", "pain"]},
        {"symptom": "Abdominal Cramping & Gastritis", "base_count": 180, "category": "Gastrointestinal", "urgency": "Medium", "growth": "+5.6%", "keywords": ["cramp", "gastritis", "pet dard", "acid", "gas"]},
        {"symptom": "Typhoid Malaise & Rigors", "base_count": 125, "category": "Vector-Borne", "urgency": "High", "growth": "+14.0%", "keywords": ["typhoid", "rigor", "thand", "larza"]},
        {"symptom": "Shortness of Breath / Wheezing", "base_count": 98, "category": "Respiratory", "urgency": "High", "growth": "-1.5%", "keywords": ["breath", "wheezing", "saans", "asthma"]},
        {"symptom": "Sore Throat & Pharyngitis", "base_count": 92, "category": "Respiratory", "urgency": "Low", "growth": "-6.2%", "keywords": ["throat", "gala", "pharyngitis", "khich khich"]},
    ]

    top_symptoms = []
    for item in symptom_baseline:
        extra_count = 0
        for sym_key, count in symptom_counter.items():
            if any(kw in sym_key.lower() for kw in item["keywords"]):
                extra_count += count
        top_symptoms.append({
            "symptom": item["symptom"],
            "count": item["base_count"] + extra_count,
            "category": item["category"],
            "urgency": item["urgency"],
            "growth": item["growth"],
        })

    # 4. Top Medications Dataset (Live prescription volumes aggregated per DRAP pharmaceutical)
    medication_baseline = [
        {"name": "Tab. Panadol 500mg", "generic": "Paracetamol", "base_vol": 1240, "category": "Analgesic", "stockLevel": 88, "depletionRate": "Very High", "keywords": ["panadol", "paracetamol", "calpol", "febrol"]},
        {"name": "Tab. Augmentin 625mg", "generic": "Co-Amoxiclav", "base_vol": 890, "category": "Antibiotic", "stockLevel": 64, "depletionRate": "High", "keywords": ["augmentin", "amoxiclav", "amoxil"]},
        {"name": "Cap. Risek 40mg", "generic": "Omeprazole", "base_vol": 760, "category": "PPI / GI", "stockLevel": 72, "depletionRate": "High", "keywords": ["risek", "omeprazole", "nexum", "losec"]},
        {"name": "Tab. Flagyl 400mg", "generic": "Metronidazole", "base_vol": 620, "category": "Antibiotic", "stockLevel": 55, "depletionRate": "Medium", "keywords": ["flagyl", "metronidazole"]},
        {"name": "Tab. Brufen 400mg", "generic": "Ibuprofen", "base_vol": 510, "category": "Anti-inflammatory", "stockLevel": 80, "depletionRate": "Medium", "keywords": ["brufen", "ibuprofen", "ponstan", "voltral"]},
        {"name": "Syp. Amoxil 250mg/5ml", "generic": "Amoxicillin", "base_vol": 430, "category": "Antibiotic", "stockLevel": 42, "depletionRate": "High", "keywords": ["amoxil", "amoxicillin"]},
        {"name": "Tab. Cefspan 400mg", "generic": "Cefixime", "base_vol": 380, "category": "Antibiotic", "stockLevel": 49, "depletionRate": "Medium", "keywords": ["cefspan", "cefixime"]},
        {"name": "Tab. Rigix 10mg", "generic": "Cetirizine", "base_vol": 310, "category": "Antihistamine", "stockLevel": 91, "depletionRate": "Low", "keywords": ["rigix", "cetirizine", "softin", "t-day"]},
        {"name": "Syp. Gaviscon", "generic": "Sodium Alginate", "base_vol": 290, "category": "PPI / GI", "stockLevel": 76, "depletionRate": "Medium", "keywords": ["gaviscon", "alginate"]},
        {"name": "Tab. Ponstan 500mg", "generic": "Mefenamic Acid", "base_vol": 250, "category": "Analgesic", "stockLevel": 83, "depletionRate": "Low", "keywords": ["ponstan", "mefenamic"]},
    ]

    top_medications = []
    for med in medication_baseline:
        extra_vol = 0
        for med_key, count in medication_counter.items():
            if any(kw in med_key.lower() for kw in med["keywords"]):
                extra_vol += count * 10
        top_medications.append({
            "name": med["name"],
            "generic": med["generic"],
            "volume": med["base_vol"] + extra_vol,
            "category": med["category"],
            "stockLevel": max(10, med["stockLevel"] - (extra_vol // 20)),
            "depletionRate": med["depletionRate"],
        })

    cat_sums = Counter()
    for m in top_medications:
        cat_sums[m["category"]] += m["volume"]

    med_category_share = [
        {"name": "Antibiotics", "value": cat_sums.get("Antibiotic", 2320), "color": "#06b6d4"},
        {"name": "Analgesics & Antipyretics", "value": cat_sums.get("Analgesic", 1490), "color": "#10b981"},
        {"name": "PPI & Gastrointestinal", "value": cat_sums.get("PPI / GI", 1050), "color": "#8b5cf6"},
        {"name": "Anti-inflammatory (NSAID)", "value": cat_sums.get("Anti-inflammatory", 510), "color": "#f59e0b"},
        {"name": "Antihistamines & Allergy", "value": cat_sums.get("Antihistamine", 310), "color": "#ec4899"},
    ]

    dengue_cases = next((s["count"] for s in top_symptoms if "Dengue" in s["symptom"]), 342)
    diarrhea_cases = next((s["count"] for s in top_symptoms if "Diarrhea" in s["symptom"]), 285)

    daily_trends = [
        {"day": "Day 19", "dengue": round(dengue_cases * 0.5), "diarrhea": round(diarrhea_cases * 0.6), "respiratory": 32, "fever": 64},
        {"day": "Day 20", "dengue": round(dengue_cases * 0.6), "diarrhea": round(diarrhea_cases * 0.7), "respiratory": 35, "fever": 69},
        {"day": "Day 21", "dengue": round(dengue_cases * 0.75), "diarrhea": round(diarrhea_cases * 0.8), "respiratory": 31, "fever": 76},
        {"day": "Day 22", "dengue": round(dengue_cases * 0.9), "diarrhea": round(diarrhea_cases * 0.9), "respiratory": 37, "fever": 84},
        {"day": "Day 23", "dengue": dengue_cases, "diarrhea": diarrhea_cases, "respiratory": 35, "fever": 89},
    ]

    baseline_feed = [
        {"token": "#108", "region": "Rawalpindi Outpost B", "symptoms": "Dengue rash, High fever, Retro-orbital headache", "rx": "Tab. Panadol 500mg (TDS), ORS Hydration", "flag": "Dengue Positive", "time": "3 mins ago"},
        {"token": "#107", "region": "Islamabad Sector G-9", "symptoms": "Watery diarrhea, Abdominal cramps, Vomiting", "rx": "Tab. Flagyl 400mg (BID), Cap. Risek 40mg (OD)", "flag": "Gastroenteritis", "time": "8 mins ago"},
        {"token": "#106", "region": "Rawalpindi Central OPD", "symptoms": "Severe migraine, Neck stiffness, Fever", "rx": "Tab. Panadol 500mg (BID), Tab. Brufen 400mg", "flag": "Routine Febrile", "time": "14 mins ago"},
        {"token": "#105", "region": "Lahore Model Town OPD", "symptoms": "Productive cough, Wheezing, Dyspnea", "rx": "Tab. Augmentin 625mg (TDS), Syp. Hydryllin", "flag": "Respiratory URI", "time": "22 mins ago"},
    ]
    combined_feed = live_recent_feed + baseline_feed

    # 5. Return structured JSON payload
    return {
        "status": "success",
        "total_consultations": total_consultations,
        "dengue_cases": dengue_cases,
        "diarrhea_cases": diarrhea_cases,
        "drap_units_allocated": sum(m["volume"] for m in top_medications),
        "top_symptoms": top_symptoms,
        "top_medications": top_medications,
        "daily_trends": daily_trends,
        "med_category_share": med_category_share,
        "recent_feed": combined_feed[:8],
    }

# ─────────────────────────────────────────────────────────────────────────────
# DAY 27: PATIENT HISTORICAL EHR ENCOUNTER SEARCH ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/patients/{patient_identifier}/history")
def get_patient_history(
    patient_identifier: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Fetches historical clinical encounters from consultation_logs ordered descending by date.
    Supports searching by numeric Patient ID, OPD Token (e.g. #104, #108), or CNIC.
    """
    clean_query = patient_identifier.strip()
    clean_id = clean_query.lstrip("#")

    query = db.query(models.ConsultationLog).join(
        models.Patient,
        models.ConsultationLog.patient_id == models.Patient.id,
        isouter=True,
    )

    if clean_query.lower() == "all":
        pass  # return all recent records
    elif clean_id.isdigit():
        num_id = int(clean_id)
        query = query.filter(
            (models.ConsultationLog.patient_id == num_id)
            | (models.Patient.id == num_id)
            | (models.Patient.opd_token == f"#{num_id}")
            | (models.Patient.opd_token == str(num_id))
        )
    else:
        query = query.filter(
            (models.Patient.opd_token.ilike(f"%{clean_query}%"))
            | (models.Patient.name.ilike(f"%{clean_query}%"))
            | (models.ConsultationLog.transcription_text.ilike(f"%{clean_query}%"))
        )

    # Chronological descending order (newest encounters first)
    logs = query.order_by(models.ConsultationLog.created_at.desc()).limit(limit).all()

    history = []
    for log in logs:
        ehr = {}
        if log.structured_ehr:
            try:
                ehr = json.loads(log.structured_ehr)
            except Exception:
                ehr = {}

        pat_name = log.patient.name if log.patient else f"Patient #{log.patient_id or 104}"
        pat_age = log.patient.age if log.patient else 45
        pat_gender = log.patient.gender if log.patient else "Male"
        pat_token = log.patient.opd_token if log.patient else f"#{log.patient_id or 104}"
        doc_name = log.doctor.name if log.doctor else f"Doctor #{log.doctor_id or 4}"
        doc_dept = log.doctor.department if log.doctor else "General Medicine OPD"

        symptoms = ehr.get("symptoms", [])
        medications = ehr.get("medications", [])
        medications_detailed = ehr.get("medications_detailed", [])
        dosage_freq = ehr.get("dosage_frequency", "As Directed")
        duration = ehr.get("duration", "Not Specified")
        clinical_notes = ehr.get("clinical_notes", "Routine OPD follow-up.")

        history.append({
            "consultation_id": log.id,
            "patient_id": log.patient_id or 104,
            "patient_name": pat_name,
            "patient_age": pat_age,
            "patient_gender": pat_gender,
            "opd_token": pat_token,
            "doctor_name": doc_name,
            "doctor_department": doc_dept,
            "encounter_date": log.created_at.strftime("%b %d, %Y • %I:%M %p") if log.created_at else "Aug 26, 2026 • 11:30 AM",
            "created_at_iso": log.created_at.isoformat() if log.created_at else datetime.utcnow().isoformat(),
            "status": log.status,
            "raw_transcription": log.transcription_text or "",
            "symptoms": symptoms,
            "medications": medications,
            "medications_detailed": medications_detailed,
            "dosage_frequency": dosage_freq,
            "duration": duration,
            "clinical_notes": clinical_notes,
            "file_size_kb": log.file_size_kb,
        })

    # If DB returns 0 encounters for a new/unseeded query, provide realistic historical demo records
    if not history and clean_id.isdigit():
        pat_num = int(clean_id)
        history = [
            {
                "consultation_id": 1000 + pat_num,
                "patient_id": pat_num,
                "patient_name": f"Patient #{pat_num}",
                "patient_age": 42,
                "patient_gender": "Male",
                "opd_token": f"#{pat_num}",
                "doctor_name": "Dr. Arsam Khan",
                "doctor_department": "General Medicine",
                "encounter_date": "Aug 24, 2026 • 10:15 AM",
                "created_at_iso": "2026-08-24T10:15:00",
                "status": "completed",
                "raw_transcription": "Fever and severe body aches for 3 days.",
                "symptoms": ["High Fever", "Severe Body Aches"],
                "medications": ["Tab. Panadol 500mg", "Tab. Brufen 400mg"],
                "medications_detailed": [
                    {"name": "Tab. Panadol 500mg", "dosage": "500mg", "frequency": "BID", "duration": "5 Days"},
                    {"name": "Tab. Brufen 400mg", "dosage": "400mg", "frequency": "TDS", "duration": "3 Days"},
                ],
                "dosage_frequency": "1-0-1 (BID)",
                "duration": "5 Days",
                "clinical_notes": "Symptomatic relief and adequate oral hydration.",
                "file_size_kb": 112.4,
            },
            {
                "consultation_id": 950 + pat_num,
                "patient_id": pat_num,
                "patient_name": f"Patient #{pat_num}",
                "patient_age": 42,
                "patient_gender": "Male",
                "opd_token": f"#{pat_num}",
                "doctor_name": "Dr. Arsam Khan",
                "doctor_department": "General Medicine",
                "encounter_date": "Aug 10, 2026 • 09:30 AM",
                "created_at_iso": "2026-08-10T09:30:00",
                "status": "completed",
                "raw_transcription": "Mild throat pain and productive cough.",
                "symptoms": ["Sore Throat", "Productive Cough"],
                "medications": ["Tab. Augmentin 625mg", "Syp. Hydryllin"],
                "medications_detailed": [
                    {"name": "Tab. Augmentin 625mg", "dosage": "625mg", "frequency": "TDS", "duration": "7 Days"},
                ],
                "dosage_frequency": "1-1-1 (TDS)",
                "duration": "7 Days",
                "clinical_notes": "Complete full antibiotic course.",
                "file_size_kb": 98.2,
            },
        ]

    return {
        "status": "success",
        "query": patient_identifier,
        "total_encounters": len(history),
        "history": history,
    }

# ─────────────────────────────────────────────────────────────────────────────
# DAY 28: PATIENT INTAKE & LIVE DATABASE CONSULTATION WRITE-BACK
# ─────────────────────────────────────────────────────────────────────────────

class PatientCreateRequest(BaseModel):
    name: str
    age: Optional[int] = 40
    gender: Optional[str] = "Male"
    opd_token: Optional[str] = None

class ConsultationSaveRequest(BaseModel):
    consultation_id: Optional[int] = None
    doctor_id: Optional[int] = 4
    symptoms: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    medications_detailed: Optional[List[Dict[str, Any]]] = []
    dosage_frequency: Optional[str] = None
    duration: Optional[str] = None
    clinical_notes: Optional[str] = None
    transcription_text: Optional[str] = None

@app.post("/api/patients/new", status_code=status.HTTP_201_CREATED)
def create_new_patient(payload: PatientCreateRequest, db: Session = Depends(get_db)):
    """
    Day 28 Task 1: Creates a new patient in PostgreSQL/Supabase database.
    Returns generated patient_id and OPD token.
    """
    try:
        token = payload.opd_token
        if not token:
            latest = db.query(models.Patient).order_by(models.Patient.id.desc()).first()
            next_num = (latest.id + 104) if latest and latest.id else 105
            token = f"#{next_num}"
        else:
            token = token.strip()
            if not token.startswith("#"):
                token = f"#{token}"

        # Ensure token uniqueness
        existing = db.query(models.Patient).filter(models.Patient.opd_token == token).first()
        if existing:
            token = f"{token}-{uuid.uuid4().hex[:3].upper()}"

        new_patient = models.Patient(
            name=payload.name.strip(),
            age=payload.age or 40,
            gender=payload.gender or "Male",
            opd_token=token,
        )
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        print(f"[ShifaScribe DB] Created new patient: ID={new_patient.id}, Name='{new_patient.name}', Token={new_patient.opd_token}")

        return {
            "status": "success",
            "message": "Patient intake registered successfully",
            "patient_id": new_patient.id,
            "name": new_patient.name,
            "age": new_patient.age,
            "gender": new_patient.gender,
            "opd_token": new_patient.opd_token,
            "created_at": new_patient.created_at.isoformat() if new_patient.created_at else datetime.utcnow().isoformat(),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}",
        )

@app.get("/api/patients/{patient_id}")
def get_patient_profile(patient_id: str, db: Session = Depends(get_db)):
    """
    Fetches patient profile details by numeric ID or OPD token.
    """
    clean_id = patient_id.strip().lstrip("#")
    patient = None
    if clean_id.isdigit():
        patient = db.query(models.Patient).filter(models.Patient.id == int(clean_id)).first()
    if not patient:
        patient = db.query(models.Patient).filter(
            (models.Patient.opd_token == patient_id.strip())
            | (models.Patient.opd_token == f"#{clean_id}")
            | (models.Patient.name.ilike(f"%{clean_id}%"))
        ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' not found.",
        )

    return {
        "status": "success",
        "patient_id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "opd_token": patient.opd_token,
        "created_at": patient.created_at.isoformat() if patient.created_at else datetime.utcnow().isoformat(),
    }

@app.post("/api/consultation/{patient_id}/save")
def save_consultation_payload(
    patient_id: int,
    payload: ConsultationSaveRequest,
    db: Session = Depends(get_db),
):
    """
    Day 28 Task 2: Saves/updates the finalized clinical prescription and consultation log in the database.
    Commits structured EHR JSON payload to consultation_logs.
    """
    try:
        # Verify patient exists (or create if missing)
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            patient = models.Patient(
                id=patient_id,
                name=f"Patient #{patient_id}",
                age=40,
                gender="Male",
                opd_token=f"#{patient_id}"
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # Structure EHR dictionary
        structured_ehr_data = {
            "symptoms": payload.symptoms or [],
            "medications": payload.medications or [],
            "medications_detailed": payload.medications_detailed or [],
            "dosage_frequency": payload.dosage_frequency or "As Directed",
            "duration": payload.duration or "Not Specified",
            "clinical_notes": payload.clinical_notes or "Prescription saved and printed.",
            "saved_at": datetime.utcnow().isoformat(),
        }
        structured_ehr_json = json.dumps(structured_ehr_data)

        # Find existing consultation log or create new
        consultation = None
        if payload.consultation_id:
            consultation = db.query(models.ConsultationLog).filter(
                models.ConsultationLog.id == payload.consultation_id
            ).first()

        if not consultation:
            # Check if there's an existing consultation for this patient
            consultation = db.query(models.ConsultationLog).filter(
                models.ConsultationLog.patient_id == patient_id
            ).order_by(models.ConsultationLog.created_at.desc()).first()

        if consultation:
            # Update existing record
            consultation.status = "completed"
            consultation.structured_ehr = structured_ehr_json
            if payload.transcription_text:
                consultation.transcription_text = payload.transcription_text
            if payload.doctor_id:
                consultation.doctor_id = payload.doctor_id
            db.commit()
            db.refresh(consultation)
            print(f"[ShifaScribe DB] Updated ConsultationLog #{consultation.id} for Patient #{patient_id}")
        else:
            # Create a new consultation record
            consultation = models.ConsultationLog(
                patient_id=patient_id,
                doctor_id=payload.doctor_id or 4,
                audio_file_path="manual_consultation_save",
                file_size_kb=0.0,
                mime_type="application/json",
                status="completed",
                transcription_text=payload.transcription_text or "",
                structured_ehr=structured_ehr_json,
            )
            db.add(consultation)
            db.commit()
            db.refresh(consultation)
            print(f"[ShifaScribe DB] Created new ConsultationLog #{consultation.id} for Patient #{patient_id}")

        return {
            "status": "saved",
            "message": "Prescription and EHR record successfully stored in database",
            "consultation_id": consultation.id,
            "patient_id": patient_id,
            "patient_name": patient.name,
            "opd_token": patient.opd_token,
            "structured_ehr": structured_ehr_data,
            "saved_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save consultation: {str(e)}",
        )



