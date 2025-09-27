"""
Enhanced patient history and Q&A endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.patient_history import (
    PatientActivityCreate, PatientActivityResponse,
    PatientVisitCreate, PatientVisitUpdate, PatientVisitResponse,
    PatientTimelineCreate, PatientTimelineResponse,
    ComprehensivePatientHistory
)
from app.services.patient_history_service import PatientHistoryService
from app.services.enhanced_ai_service import EnhancedAIService, SafeQAResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize enhanced AI service
enhanced_ai_service = EnhancedAIService()

@router.get("/patients/{patient_id}/comprehensive-history")
async def get_comprehensive_patient_history(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive patient history for Q&A interface."""
    try:
        from app.services.patient_service import PatientService
        from app.models.patient import Patient, MedicalRecord, DischargeNote
        
        patient_service = PatientService(db)
        
        # Get patient data
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get medical records
        medical_records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
        
        # Get discharge notes
        discharge_notes = db.query(DischargeNote).filter(DischargeNote.patient_id == patient_id).all()
        
        # Get activities and visits (if they exist)
        try:
            activities = db.query(PatientActivity).filter(PatientActivity.patient_id == patient_id).limit(20).all()
        except:
            activities = []
            
        try:
            visits = db.query(PatientVisit).filter(PatientVisit.patient_id == patient_id).all()
        except:
            visits = []
            
        try:
            timeline = db.query(PatientTimeline).filter(PatientTimeline.patient_id == patient_id).limit(50).all()
        except:
            timeline = []
        
        # Convert to response format
        patient_dict = {
            "id": patient.id,
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "gender": patient.gender,
            "phone": patient.phone,
            "email": patient.email,
            "emergency_contact": patient.emergency_contact,
            "medical_history": patient.medical_history or [],
            "allergies": patient.allergies or [],
            "current_medications": patient.current_medications or [],
            "created_at": patient.created_at.isoformat() if patient.created_at else None,
            "updated_at": patient.updated_at.isoformat() if patient.updated_at else None
        }
        
        medical_records_list = []
        for record in medical_records:
            medical_records_list.append({
                "id": record.id,
                "patient_id": record.patient_id,
                "admission_date": record.admission_date.isoformat() if record.admission_date else None,
                "discharge_date": record.discharge_date.isoformat() if record.discharge_date else None,
                "primary_diagnosis": record.primary_diagnosis,
                "secondary_diagnoses": record.secondary_diagnoses or [],
                "procedures_performed": record.procedures_performed or [],
                "treatment_summary": record.treatment_summary,
                "physician_notes": record.physician_notes,
                "nursing_notes": record.nursing_notes,
                "lab_results": record.lab_results or [],
                "vital_signs": record.vital_signs or [],
                "severity_level": record.severity_level,
                "created_at": record.created_at.isoformat() if record.created_at else None
            })
        
        discharge_notes_list = []
        for note in discharge_notes:
            discharge_notes_list.append({
                "id": note.id,
                "patient_id": note.patient_id,
                "medical_record_id": note.medical_record_id,
                "discharge_summary": note.discharge_summary,
                "medications_at_discharge": note.medications_at_discharge or [],
                "follow_up_instructions": note.follow_up_instructions,
                "activity_restrictions": note.activity_restrictions,
                "diet_instructions": note.diet_instructions,
                "warning_signs": note.warning_signs,
                "discharge_physician": note.discharge_physician,
                "discharge_date": note.discharge_date.isoformat() if note.discharge_date else None,
                "created_at": note.created_at.isoformat() if note.created_at else None
            })
        
        # Simple response structure
        response = {
            "patient": patient_dict,
            "visits": [],  # Will be populated when visits table is working
            "activities": [],  # Will be populated when activities table is working
            "timeline": [],  # Will be populated when timeline table is working
            "medical_records": medical_records_list,
            "discharge_notes": discharge_notes_list,
            "total_visits": len(visits),
            "total_days_in_hospital": 0,
            "last_visit_date": None,
            "current_status": "outpatient"
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comprehensive history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving patient history"
        )

@router.post("/ask-question-enhanced/{patient_id}")
async def ask_question_enhanced(
    patient_id: str,
    request_body: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Enhanced Q&A with PII protection and safety measures."""
    try:
        question = request_body.get("question")
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is required"
            )
        
        from app.services.patient_service import PatientService
        
        # Get patient data using existing service
        patient_service = PatientService(db)
        patient = patient_service.get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check if AI service is available
        if not enhanced_ai_service.client:
            return {
                "question": question,
                "answer": "LLM not available. Please try again later or contact your healthcare provider.",
                "confidence": 0.0,
                "safety_flags": ["llm_unavailable"],
                "sources": ["System status"],
                "disclaimer": "AI language model is currently unavailable."
            }
        
        # Get medical records and discharge notes for comprehensive context
        from app.models.patient import MedicalRecord, DischargeNote
        
        medical_records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()
        discharge_notes = db.query(DischargeNote).filter(DischargeNote.patient_id == patient_id).all()
        
        # Create comprehensive patient context with actual data
        medical_records_data = []
        for record in medical_records:
            medical_records_data.append({
                "primary_diagnosis": record.primary_diagnosis,
                "secondary_diagnoses": record.secondary_diagnoses or [],
                "procedures_performed": record.procedures_performed or [],
                "treatment_summary": record.treatment_summary,
                "physician_notes": record.physician_notes,
                "severity_level": record.severity_level,
                "admission_date": record.admission_date.isoformat() if record.admission_date else None,
                "discharge_date": record.discharge_date.isoformat() if record.discharge_date else None
            })
        
        discharge_notes_data = []
        for note in discharge_notes:
            discharge_notes_data.append({
                "discharge_summary": note.discharge_summary,
                "medications_at_discharge": note.medications_at_discharge or [],
                "follow_up_instructions": note.follow_up_instructions,
                "activity_restrictions": note.activity_restrictions,
                "diet_instructions": note.diet_instructions,
                "warning_signs": note.warning_signs,
                "discharge_physician": note.discharge_physician
            })
        
        patient_context = {
            "patient": {
                "age_group": "adult",  # Simplified for privacy
                "gender": patient.gender,
                "medical_history": patient.medical_history or [],
                "allergies": patient.allergies or [],
                "current_medications": patient.current_medications or []
            },
            "medical_records": medical_records_data,
            "discharge_notes": discharge_notes_data,
            "activities": [],
            "timeline": [],
            "visits": [],
            "total_visits": len(medical_records),
            "current_status": "outpatient"
        }
        
        # Get AI response with safety measures - LLM only, no fallbacks
        try:
            response = enhanced_ai_service.answer_patient_question(
                question=question,
                patient_history=patient_context,
                context_type="comprehensive"
            )
            return response
        except Exception as ai_error:
            logger.error(f"LLM service error: {str(ai_error)}")
            
            # Only return LLM unavailable message, no fallback content
            return {
                "question": question,
                "answer": "LLM not available. Please try again later or contact your healthcare provider.",
                "confidence": 0.0,
                "safety_flags": ["llm_error"],
                "sources": ["System status"],
                "disclaimer": "AI language model encountered an error and is currently unavailable."
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced Q&A: {str(e)}")
        # Return LLM unavailable message only
        return {
            "question": question,
            "answer": "LLM not available. Please try again later or contact your healthcare provider.",
            "confidence": 0.0,
            "safety_flags": ["system_error"],
            "sources": ["System status"],
            "disclaimer": "System error occurred. AI language model is currently unavailable."
        }

@router.post("/patients/{patient_id}/activities", response_model=PatientActivityResponse)
async def log_patient_activity(
    patient_id: str,
    activity_data: PatientActivityCreate,
    db: Session = Depends(get_db)
):
    """Log a patient activity for audit trail."""
    try:
        history_service = PatientHistoryService(db)
        activity = history_service.log_activity(activity_data)
        return activity
        
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging activity"
        )

@router.get("/patients/{patient_id}/activities", response_model=List[PatientActivityResponse])
async def get_patient_activities(
    patient_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get patient activities for audit trail."""
    try:
        history_service = PatientHistoryService(db)
        activities = history_service.get_patient_activities(patient_id, limit)
        return activities
        
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving activities"
        )

@router.post("/patients/{patient_id}/visits", response_model=PatientVisitResponse)
async def create_patient_visit(
    patient_id: str,
    visit_data: PatientVisitCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient visit."""
    try:
        history_service = PatientHistoryService(db)
        visit = history_service.create_visit(visit_data)
        return visit
        
    except Exception as e:
        logger.error(f"Error creating visit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating visit"
        )

@router.put("/patients/{patient_id}/visits/{visit_id}", response_model=PatientVisitResponse)
async def update_patient_visit(
    patient_id: str,
    visit_id: int,
    visit_data: PatientVisitUpdate,
    db: Session = Depends(get_db)
):
    """Update a patient visit."""
    try:
        history_service = PatientHistoryService(db)
        visit = history_service.update_visit(visit_id, visit_data)
        
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        
        return visit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating visit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating visit"
        )

@router.get("/patients/{patient_id}/visits", response_model=List[PatientVisitResponse])
async def get_patient_visits(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get all visits for a patient."""
    try:
        history_service = PatientHistoryService(db)
        visits = history_service.get_patient_visits(patient_id)
        return visits
        
    except Exception as e:
        logger.error(f"Error getting visits: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving visits"
        )

@router.post("/patients/{patient_id}/timeline", response_model=PatientTimelineResponse)
async def add_timeline_event(
    patient_id: str,
    timeline_data: PatientTimelineCreate,
    db: Session = Depends(get_db)
):
    """Add an event to patient timeline."""
    try:
        history_service = PatientHistoryService(db)
        timeline_event = history_service.add_timeline_event(timeline_data)
        return timeline_event
        
    except Exception as e:
        logger.error(f"Error adding timeline event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding timeline event"
        )

@router.get("/patients/{patient_id}/timeline", response_model=List[PatientTimelineResponse])
async def get_patient_timeline(
    patient_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get patient timeline events."""
    try:
        history_service = PatientHistoryService(db)
        timeline = history_service.get_patient_timeline(patient_id, limit)
        return timeline
        
    except Exception as e:
        logger.error(f"Error getting timeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving timeline"
        )

@router.get("/patients/{patient_id}/safe-summary")
async def get_safe_patient_summary(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get PII-safe patient summary for AI processing."""
    try:
        history_service = PatientHistoryService(db)
        comprehensive_history = history_service.get_comprehensive_history(patient_id)
        
        if not comprehensive_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Generate safe summary
        patient_history_dict = comprehensive_history.dict()
        safe_summary = enhanced_ai_service.generate_safe_discharge_summary(patient_history_dict)
        
        return {
            "patient_id": patient_id,
            "safe_summary": safe_summary,
            "generated_at": datetime.utcnow().isoformat(),
            "privacy_protected": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating safe summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating safe summary"
        )
