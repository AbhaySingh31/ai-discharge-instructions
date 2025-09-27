"""
Enhanced patient history and audit trail models.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum

from app.core.database import Base

class ActivityType(str, Enum):
    """Types of patient activities for audit trail."""
    ADMISSION = "admission"
    DISCHARGE = "discharge"
    UPDATE = "update"
    MEDICATION_ADDED = "medication_added"
    MEDICATION_REMOVED = "medication_removed"
    DIAGNOSIS_UPDATED = "diagnosis_updated"
    PROCEDURE_PERFORMED = "procedure_performed"
    VISIT_SCHEDULED = "visit_scheduled"
    VISIT_COMPLETED = "visit_completed"
    INSTRUCTION_GENERATED = "instruction_generated"
    QUESTION_ASKED = "question_asked"

class PatientActivity(Base):
    """Audit trail for all patient activities."""
    __tablename__ = "patient_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    activity_type = Column(String, nullable=False)  # ActivityType enum value
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional structured data
    performed_by = Column(String, nullable=True)  # User/system that performed the action
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class PatientVisit(Base):
    """Track individual patient visits/stays."""
    __tablename__ = "patient_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    visit_number = Column(String, nullable=False, unique=True)  # e.g., "V001", "V002"
    
    # Visit details
    admission_date = Column(DateTime, nullable=False)
    discharge_date = Column(DateTime, nullable=True)
    visit_type = Column(String, nullable=False)  # "emergency", "scheduled", "follow_up"
    department = Column(String, nullable=True)  # "cardiology", "surgery", etc.
    attending_physician = Column(String, nullable=True)
    
    # Visit status
    status = Column(String, default="active")  # "active", "discharged", "transferred"
    
    # Visit summary
    chief_complaint = Column(Text, nullable=True)
    visit_summary = Column(Text, nullable=True)
    discharge_disposition = Column(String, nullable=True)  # "home", "rehab", "transfer"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PatientTimeline(Base):
    """Comprehensive timeline of patient events."""
    __tablename__ = "patient_timeline"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    visit_id = Column(Integer, ForeignKey("patient_visits.id"), nullable=True)
    
    # Event details
    event_type = Column(String, nullable=False)  # "admission", "procedure", "medication", etc.
    event_title = Column(String, nullable=False)
    event_description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    
    # Event metadata
    severity = Column(String, nullable=True)  # "low", "medium", "high", "critical"
    category = Column(String, nullable=True)  # "clinical", "administrative", "medication"
    performed_by = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Additional data
    event_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models for API

class PatientActivityCreate(BaseModel):
    patient_id: str
    activity_type: ActivityType
    description: str
    details: Optional[Dict[str, Any]] = None
    performed_by: Optional[str] = None

class PatientActivityResponse(BaseModel):
    id: int
    patient_id: str
    activity_type: str
    description: str
    details: Optional[Dict[str, Any]]
    performed_by: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PatientVisitCreate(BaseModel):
    patient_id: str
    visit_number: str
    admission_date: datetime
    visit_type: str
    department: Optional[str] = None
    attending_physician: Optional[str] = None
    chief_complaint: Optional[str] = None

class PatientVisitUpdate(BaseModel):
    discharge_date: Optional[datetime] = None
    status: Optional[str] = None
    visit_summary: Optional[str] = None
    discharge_disposition: Optional[str] = None
    attending_physician: Optional[str] = None

class PatientVisitResponse(BaseModel):
    id: int
    patient_id: str
    visit_number: str
    admission_date: datetime
    discharge_date: Optional[datetime]
    visit_type: str
    department: Optional[str]
    attending_physician: Optional[str]
    status: str
    chief_complaint: Optional[str]
    visit_summary: Optional[str]
    discharge_disposition: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PatientTimelineCreate(BaseModel):
    patient_id: str
    visit_id: Optional[int] = None
    event_type: str
    event_title: str
    event_description: Optional[str] = None
    event_date: datetime
    severity: Optional[str] = None
    category: Optional[str] = None
    performed_by: Optional[str] = None
    location: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None

class PatientTimelineResponse(BaseModel):
    id: int
    patient_id: str
    visit_id: Optional[int]
    event_type: str
    event_title: str
    event_description: Optional[str]
    event_date: datetime
    severity: Optional[str]
    category: Optional[str]
    performed_by: Optional[str]
    location: Optional[str]
    event_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ComprehensivePatientHistory(BaseModel):
    """Complete patient history for Q&A interface."""
    patient: Dict[str, Any]
    visits: List[PatientVisitResponse]
    activities: List[PatientActivityResponse]
    timeline: List[PatientTimelineResponse]
    medical_records: List[Dict[str, Any]]
    discharge_notes: List[Dict[str, Any]]
    total_visits: int
    total_days_in_hospital: int
    last_visit_date: Optional[datetime]
    current_status: str
