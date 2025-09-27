from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.core.database import Base

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"

class SeverityEnum(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

# SQLAlchemy Models
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    emergency_contact = Column(JSON)
    medical_history = Column(JSON)
    allergies = Column(JSON)
    current_medications = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False, index=True)
    admission_date = Column(DateTime, nullable=False)
    discharge_date = Column(DateTime)
    primary_diagnosis = Column(String, nullable=False)
    secondary_diagnoses = Column(JSON)
    procedures_performed = Column(JSON)
    treatment_summary = Column(Text)
    physician_notes = Column(Text)
    nursing_notes = Column(Text)
    lab_results = Column(JSON)
    vital_signs = Column(JSON)
    severity_level = Column(String, default="moderate")
    visit_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DischargeNote(Base):
    __tablename__ = "discharge_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False, index=True)
    medical_record_id = Column(Integer, nullable=False)
    discharge_summary = Column(Text, nullable=False)
    medications_at_discharge = Column(JSON)
    follow_up_instructions = Column(Text)
    activity_restrictions = Column(Text)
    diet_instructions = Column(Text)
    warning_signs = Column(Text)
    discharge_physician = Column(String)
    discharge_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Models for API
class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None

class Allergy(BaseModel):
    allergen: str
    reaction: str
    severity: SeverityEnum

class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    route: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    instructions: Optional[str] = None

class VitalSigns(BaseModel):
    temperature: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    recorded_at: datetime

class LabResult(BaseModel):
    test_name: str
    value: str
    unit: str
    reference_range: str
    status: str  # normal, abnormal, critical
    recorded_at: datetime

class PatientCreate(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: GenderEnum
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[EmergencyContact] = None
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[Allergy]] = []
    current_medications: Optional[List[Medication]] = []

class PatientResponse(BaseModel):
    id: int
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    phone: Optional[str]
    email: Optional[str]
    emergency_contact: Optional[Dict[str, Any]]
    medical_history: Optional[List[str]]
    allergies: Optional[List[Dict[str, Any]]]
    current_medications: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class MedicalRecordCreate(BaseModel):
    patient_id: str
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    primary_diagnosis: str
    secondary_diagnoses: Optional[List[str]] = []
    procedures_performed: Optional[List[str]] = []
    treatment_summary: str
    physician_notes: Optional[str] = None
    nursing_notes: Optional[str] = None
    lab_results: Optional[List[LabResult]] = []
    vital_signs: Optional[List[VitalSigns]] = []
    severity_level: SeverityEnum = SeverityEnum.MODERATE

class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: str
    admission_date: datetime
    discharge_date: Optional[datetime]
    primary_diagnosis: str
    secondary_diagnoses: Optional[List[str]]
    procedures_performed: Optional[List[str]]
    treatment_summary: str
    physician_notes: Optional[str]
    nursing_notes: Optional[str]
    lab_results: Optional[List[Dict[str, Any]]]
    vital_signs: Optional[List[Dict[str, Any]]]
    severity_level: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class DischargeNoteCreate(BaseModel):
    patient_id: str
    medical_record_id: int
    discharge_summary: str
    medications_at_discharge: Optional[List[Medication]] = []
    follow_up_instructions: Optional[str] = None
    activity_restrictions: Optional[str] = None
    diet_instructions: Optional[str] = None
    warning_signs: Optional[str] = None
    discharge_physician: str
    discharge_date: datetime

class DischargeNoteResponse(BaseModel):
    id: int
    patient_id: str
    medical_record_id: int
    discharge_summary: str
    medications_at_discharge: Optional[List[Dict[str, Any]]]
    follow_up_instructions: Optional[str]
    activity_restrictions: Optional[str]
    diet_instructions: Optional[str]
    warning_signs: Optional[str]
    discharge_physician: str
    discharge_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
