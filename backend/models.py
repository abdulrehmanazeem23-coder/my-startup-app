from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    opd_token = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("ConsultationLog", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    room_number = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("ConsultationLog", back_populates="doctor")

class ConsultationLog(Base):
    __tablename__ = "consultation_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    audio_file_path = Column(String(255), nullable=False)
    file_size_kb = Column(Float, nullable=False)
    mime_type = Column(String(50), default="audio/webm")
    status = Column(String(50), default="recorded")
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("Doctor", back_populates="consultations")
