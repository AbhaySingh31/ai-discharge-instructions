from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.patient import (
    Patient, MedicalRecord, DischargeNote,
    PatientCreate, PatientResponse,
    MedicalRecordCreate, MedicalRecordResponse,
    DischargeNoteCreate, DischargeNoteResponse
)
from app.services.ai_agent import DischargeInstructionsAI, PersonalizedInstructions, QAResponse
from app.services.patient_service import PatientService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI service lazily
ai_service = None

def get_ai_service():
    global ai_service
    if ai_service is None:
        ai_service = DischargeInstructionsAI()
    return ai_service

@router.post("/patients/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient record."""
    try:
        patient_service = PatientService(db)
        db_patient = patient_service.create_patient(patient)
        return db_patient
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating patient: {str(e)}"
        )

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get patient by ID."""
    try:
        patient_service = PatientService(db)
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving patient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving patient"
        )

@router.get("/patients/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 1000,
    search: str = None,
    db: Session = Depends(get_db)
):
    """List all patients with pagination and optional search."""
    try:
        patient_service = PatientService(db)
        if search:
            patients = patient_service.search_patients(search)
            # Apply pagination to search results
            patients = patients[skip:skip + limit]
        else:
            patients = patient_service.get_patients(skip=skip, limit=limit)
        return patients
    except Exception as e:
        logger.error(f"Error listing patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving patients"
        )

@router.post("/medical-records/", response_model=MedicalRecordResponse)
async def create_medical_record(
    medical_record: MedicalRecordCreate,
    db: Session = Depends(get_db)
):
    """Create a new medical record."""
    try:
        patient_service = PatientService(db)
        db_record = patient_service.create_medical_record(medical_record)
        return db_record
    except Exception as e:
        logger.error(f"Error creating medical record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating medical record: {str(e)}"
        )

@router.get("/medical-records/{patient_id}", response_model=List[MedicalRecordResponse])
async def get_medical_records(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get medical records for a patient."""
    try:
        patient_service = PatientService(db)
        records = patient_service.get_medical_records_by_patient(patient_id)
        return records
    except Exception as e:
        logger.error(f"Error retrieving medical records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving medical records"
        )

@router.post("/discharge-notes/", response_model=DischargeNoteResponse)
async def create_discharge_note(
    discharge_note: DischargeNoteCreate,
    db: Session = Depends(get_db)
):
    """Create a new discharge note."""
    try:
        patient_service = PatientService(db)
        db_note = patient_service.create_discharge_note(discharge_note)
        return db_note
    except Exception as e:
        logger.error(f"Error creating discharge note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating discharge note: {str(e)}"
        )

@router.get("/discharge-notes/{patient_id}", response_model=List[DischargeNoteResponse])
async def get_discharge_notes(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get discharge notes for a patient."""
    try:
        patient_service = PatientService(db)
        notes = patient_service.get_discharge_notes_by_patient(patient_id)
        return notes
    except Exception as e:
        logger.error(f"Error retrieving discharge notes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving discharge notes"
        )

@router.post("/generate-instructions/{patient_id}", response_model=PersonalizedInstructions)
async def generate_discharge_instructions(
    patient_id: str,
    medical_record_id: int,
    db: Session = Depends(get_db)
):
    """Generate personalized discharge instructions for a patient."""
    try:
        patient_service = PatientService(db)
        
        # Get patient data
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get medical record
        medical_record = patient_service.get_medical_record_by_id(medical_record_id)
        if not medical_record or medical_record.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found for this patient"
            )
        
        # Get discharge note
        discharge_notes = patient_service.get_discharge_notes_by_medical_record(medical_record_id)
        if not discharge_notes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discharge note not found for this medical record"
            )
        
        discharge_note = discharge_notes[0]  # Get the most recent one
        
        # Convert to dictionaries for AI processing
        patient_dict = {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth.isoformat(),
            "gender": patient.gender,
            "medical_history": patient.medical_history or [],
            "allergies": patient.allergies or [],
            "current_medications": patient.current_medications or []
        }
        
        medical_record_dict = {
            "primary_diagnosis": medical_record.primary_diagnosis,
            "secondary_diagnoses": medical_record.secondary_diagnoses or [],
            "procedures_performed": medical_record.procedures_performed or [],
            "treatment_summary": medical_record.treatment_summary,
            "physician_notes": medical_record.physician_notes,
            "severity_level": medical_record.severity_level,
            "lab_results": medical_record.lab_results or [],
            "vital_signs": medical_record.vital_signs or []
        }
        
        discharge_note_dict = {
            "discharge_summary": discharge_note.discharge_summary,
            "medications_at_discharge": discharge_note.medications_at_discharge or [],
            "follow_up_instructions": discharge_note.follow_up_instructions,
            "activity_restrictions": discharge_note.activity_restrictions,
            "diet_instructions": discharge_note.diet_instructions,
            "warning_signs": discharge_note.warning_signs,
            "discharge_physician": discharge_note.discharge_physician
        }
        
        # Generate personalized instructions using AI
        if not get_ai_service().client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. OpenRouter API key is not configured."
            )
        
        instructions = get_ai_service().generate_personalized_instructions(
            patient_dict,
            medical_record_dict,
            discharge_note_dict
        )
        return instructions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating discharge instructions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating discharge instructions"
        )

@router.post("/ask-question/{patient_id}", response_model=QAResponse)
async def ask_question(
    patient_id: str,
    question: str,
    medical_record_id: int,
    db: Session = Depends(get_db)
):
    """Answer patient questions about their discharge instructions."""
    try:
        patient_service = PatientService(db)
        
        # Get patient data
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get medical record
        medical_record = patient_service.get_medical_record_by_id(medical_record_id)
        if not medical_record or medical_record.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found for this patient"
            )
        
        # Get discharge note
        discharge_notes = patient_service.get_discharge_notes_by_medical_record(medical_record_id)
        if not discharge_notes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discharge note not found for this medical record"
            )
        
        discharge_note = discharge_notes[0]
        
        # Prepare context
        patient_context = {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "diagnosis": medical_record.primary_diagnosis,
            "medications": discharge_note.medications_at_discharge or [],
            "allergies": patient.allergies or []
        }
        
        # Generate discharge instructions first (needed for context)
        patient_dict = {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth.isoformat(),
            "gender": patient.gender,
            "medical_history": patient.medical_history or [],
            "allergies": patient.allergies or [],
            "current_medications": patient.current_medications or []
        }
        
        medical_record_dict = {
            "primary_diagnosis": medical_record.primary_diagnosis,
            "secondary_diagnoses": medical_record.secondary_diagnoses or [],
            "procedures_performed": medical_record.procedures_performed or [],
            "treatment_summary": medical_record.treatment_summary,
            "physician_notes": medical_record.physician_notes,
            "severity_level": medical_record.severity_level,
            "lab_results": medical_record.lab_results or [],
            "vital_signs": medical_record.vital_signs or []
        }
        
        discharge_note_dict = {
            "discharge_summary": discharge_note.discharge_summary,
            "medications_at_discharge": discharge_note.medications_at_discharge or [],
            "follow_up_instructions": discharge_note.follow_up_instructions,
            "activity_restrictions": discharge_note.activity_restrictions,
            "diet_instructions": discharge_note.diet_instructions,
            "warning_signs": discharge_note.warning_signs,
            "discharge_physician": discharge_note.discharge_physician
        }
        
        # Check if AI service is available
        if not get_ai_service().client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. OpenRouter API key is not configured."
            )
        
        instructions = get_ai_service().generate_personalized_instructions(
            patient_dict,
            medical_record_dict,
            discharge_note_dict
        )
        
        # Answer the question
        response = get_ai_service().answer_patient_question(
            question,
            patient_context,
            instructions
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering patient question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing question"
        )

@router.get("/patients/search/{query}", response_model=List[PatientResponse])
async def search_patients(
    query: str,
    db: Session = Depends(get_db)
):
    """Search patients by patient ID, name, or other criteria."""
    try:
        patient_service = PatientService(db)
        patients = patient_service.search_patients(query)
        return patients
    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching patients"
        )

@router.post("/generate-quick-discharge/{patient_id}")
async def generate_quick_discharge_summary(
    patient_id: str,
    medical_record_id: int = None,
    db: Session = Depends(get_db)
):
    """Generate a quick discharge summary without full AI processing."""
    try:
        patient_service = PatientService(db)
        
        # Get patient data
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get medical record
        medical_record = patient_service.get_medical_record_by_id(medical_record_id)
        if not medical_record or medical_record.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found for this patient"
            )
        
        # Generate a basic discharge summary
        summary = f"""
DISCHARGE SUMMARY

Patient: {patient.first_name} {patient.last_name}
Patient ID: {patient.patient_id}
Date of Birth: {patient.date_of_birth.strftime('%Y-%m-%d')}
Gender: {patient.gender.title()}

ADMISSION INFORMATION:
Admission Date: {medical_record.admission_date.strftime('%Y-%m-%d')}
Discharge Date: {medical_record.discharge_date.strftime('%Y-%m-%d') if medical_record.discharge_date else 'Not discharged'}
Primary Diagnosis: {medical_record.primary_diagnosis}
Secondary Diagnoses: {', '.join(medical_record.secondary_diagnoses or [])}

TREATMENT SUMMARY:
{medical_record.treatment_summary}

PROCEDURES PERFORMED:
{', '.join(medical_record.procedures_performed or [])}

CURRENT MEDICATIONS:
{chr(10).join([f"- {med['name']} {med['dosage']} {med['frequency']}" for med in patient.current_medications or []])}

ALLERGIES:
{chr(10).join([f"- {allergy['allergen']}: {allergy['reaction']} ({allergy['severity']} severity)" for allergy in patient.allergies or []]) if patient.allergies else "No known allergies"}

DISCHARGE INSTRUCTIONS:
1. Continue prescribed medications as directed
2. Follow up with primary care physician within 1-2 weeks
3. Return to emergency department if symptoms worsen
4. Maintain regular diet and increase fluid intake
5. Light activity for the first week, gradually increase as tolerated

EMERGENCY CONTACT:
{patient.emergency_contact['name'] if patient.emergency_contact else 'Not provided'}
{patient.emergency_contact['phone'] if patient.emergency_contact else ''}
"""
        
        return {
            "patient_id": patient_id,
            "medical_record_id": medical_record_id,
            "discharge_summary": summary.strip(),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quick discharge summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating discharge summary"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Discharge Instructions API"}
