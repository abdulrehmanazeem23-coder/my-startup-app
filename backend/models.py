import uuid as _uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import engine, Base

# ─────────────────────────────────────────────────────────────────────────────
# Detect whether the connected database uses UUID primary keys (Supabase Cloud)
# or Integer primary keys (local Docker PostgreSQL / SQLite).
# ─────────────────────────────────────────────────────────────────────────────
_IS_SUPABASE_UUID = False
try:
    from sqlalchemy import inspect as _sa_inspect
    _insp = _sa_inspect(engine)
    if "patients" in _insp.get_table_names():
        _cols = {c["name"]: str(c["type"]) for c in _insp.get_columns("patients")}
        if "UUID" in _cols.get("id", ""):
            _IS_SUPABASE_UUID = True
except Exception:
    pass

if _IS_SUPABASE_UUID:
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    _PK_TYPE = PG_UUID(as_uuid=True)
    _PK_DEFAULT = _uuid.uuid4
    _FK_TYPE = PG_UUID(as_uuid=True)
else:
    _PK_TYPE = Integer
    _PK_DEFAULT = None
    _FK_TYPE = Integer

print(f"[ShifaScribe Models] UUID mode: {_IS_SUPABASE_UUID}")


class Patient(Base):
    __tablename__ = "patients"

    if _IS_SUPABASE_UUID:
        id = Column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4, index=True)
    else:
        id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True, default="Male")
    cnic = Column(String(50), nullable=True)
    opd_token = Column(String(50), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("ConsultationLog", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    if _IS_SUPABASE_UUID:
        id = Column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4, index=True)
    else:
        id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    specialty = Column(String(255), nullable=True)
    room_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("ConsultationLog", back_populates="doctor")


class ConsultationLog(Base):
    __tablename__ = "consultation_logs"

    if _IS_SUPABASE_UUID:
        id = Column(PG_UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4, index=True)
        patient_id = Column(PG_UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
        doctor_id = Column(PG_UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=True)
    else:
        id = Column(Integer, primary_key=True, index=True)
        patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
        doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)

    audio_file_path = Column(String(500), nullable=True, default="")
    file_size_kb = Column(Float, nullable=True, default=0.0)
    mime_type = Column(String(50), nullable=True, default="audio/webm")
    status = Column(String(50), nullable=True, default="recorded")
    # Dual-compatible columns for both Supabase native schema and ShifaScribe app schema
    raw_transcript = Column(Text, nullable=True)
    transcription_text = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True)
    structured_ehr = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("Doctor", back_populates="consultations")

