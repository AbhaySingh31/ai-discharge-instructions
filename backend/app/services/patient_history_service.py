"""
Patient history and audit trail service.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.patient import Patient, MedicalRecord, DischargeNote
from app.models.patient_history import (
    PatientActivity, PatientVisit, PatientTimeline,
    ActivityType, PatientActivityCreate, PatientVisitCreate, PatientVisitUpdate,
    PatientTimelineCreate, ComprehensivePatientHistory,
    PatientActivityResponse, PatientVisitResponse, PatientTimelineResponse
)
import logging

logger = logging.getLogger(__name__)

class PatientHistoryService:
    """Service for managing patient history, activities, and audit trails."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Activity Management
    def log_activity(self, activity_data: PatientActivityCreate) -> PatientActivity:
        """Log a patient activity for audit trail."""
        try:
            activity = PatientActivity(
                patient_id=activity_data.patient_id,
                activity_type=activity_data.activity_type.value,
                description=activity_data.description,
                details=activity_data.details,
                performed_by=activity_data.performed_by,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            
            logger.info(f"Logged activity for patient {activity_data.patient_id}: {activity_data.activity_type}")
            return activity
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging activity: {str(e)}")
            raise
    
    def get_patient_activities(self, patient_id: str, limit: int = 50) -> List[PatientActivity]:
        """Get all activities for a patient."""
        return (self.db.query(PatientActivity)
                .filter(PatientActivity.patient_id == patient_id)
                .order_by(desc(PatientActivity.timestamp))
                .limit(limit)
                .all())
    
    # Visit Management
    def create_visit(self, visit_data: PatientVisitCreate) -> PatientVisit:
        """Create a new patient visit."""
        try:
            visit = PatientVisit(
                patient_id=visit_data.patient_id,
                visit_number=visit_data.visit_number,
                admission_date=visit_data.admission_date,
                visit_type=visit_data.visit_type,
                department=visit_data.department,
                attending_physician=visit_data.attending_physician,
                chief_complaint=visit_data.chief_complaint,
                status="active"
            )
            
            self.db.add(visit)
            self.db.commit()
            self.db.refresh(visit)
            
            # Log the admission activity
            self.log_activity(PatientActivityCreate(
                patient_id=visit_data.patient_id,
                activity_type=ActivityType.ADMISSION,
                description=f"Patient admitted for {visit_data.visit_type} visit",
                details={
                    "visit_number": visit_data.visit_number,
                    "department": visit_data.department,
                    "chief_complaint": visit_data.chief_complaint
                },
                performed_by=visit_data.attending_physician
            ))
            
            logger.info(f"Created visit {visit_data.visit_number} for patient {visit_data.patient_id}")
            return visit
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating visit: {str(e)}")
            raise
    
    def update_visit(self, visit_id: int, visit_data: PatientVisitUpdate) -> Optional[PatientVisit]:
        """Update a patient visit."""
        try:
            visit = self.db.query(PatientVisit).filter(PatientVisit.id == visit_id).first()
            if not visit:
                return None
            
            # Track what's being updated
            updates = {}
            
            if visit_data.discharge_date and not visit.discharge_date:
                visit.discharge_date = visit_data.discharge_date
                visit.status = "discharged"
                updates["discharge_date"] = visit_data.discharge_date.isoformat()
                
                # Log discharge activity
                self.log_activity(PatientActivityCreate(
                    patient_id=visit.patient_id,
                    activity_type=ActivityType.DISCHARGE,
                    description=f"Patient discharged from visit {visit.visit_number}",
                    details={
                        "visit_number": visit.visit_number,
                        "discharge_disposition": visit_data.discharge_disposition
                    },
                    performed_by=visit_data.attending_physician
                ))
            
            if visit_data.status:
                visit.status = visit_data.status
                updates["status"] = visit_data.status
            
            if visit_data.visit_summary:
                visit.visit_summary = visit_data.visit_summary
                updates["visit_summary"] = "Updated"
            
            if visit_data.discharge_disposition:
                visit.discharge_disposition = visit_data.discharge_disposition
                updates["discharge_disposition"] = visit_data.discharge_disposition
            
            if visit_data.attending_physician:
                visit.attending_physician = visit_data.attending_physician
                updates["attending_physician"] = visit_data.attending_physician
            
            visit.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(visit)
            
            # Log update activity if there were changes
            if updates:
                self.log_activity(PatientActivityCreate(
                    patient_id=visit.patient_id,
                    activity_type=ActivityType.UPDATE,
                    description=f"Visit {visit.visit_number} updated",
                    details=updates,
                    performed_by=visit_data.attending_physician
                ))
            
            logger.info(f"Updated visit {visit.visit_number}")
            return visit
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating visit: {str(e)}")
            raise
    
    def get_patient_visits(self, patient_id: str) -> List[PatientVisit]:
        """Get all visits for a patient."""
        return (self.db.query(PatientVisit)
                .filter(PatientVisit.patient_id == patient_id)
                .order_by(desc(PatientVisit.admission_date))
                .all())
    
    # Timeline Management
    def add_timeline_event(self, timeline_data: PatientTimelineCreate) -> PatientTimeline:
        """Add an event to patient timeline."""
        try:
            timeline_event = PatientTimeline(
                patient_id=timeline_data.patient_id,
                visit_id=timeline_data.visit_id,
                event_type=timeline_data.event_type,
                event_title=timeline_data.event_title,
                event_description=timeline_data.event_description,
                event_date=timeline_data.event_date,
                severity=timeline_data.severity,
                category=timeline_data.category,
                performed_by=timeline_data.performed_by,
                location=timeline_data.location,
                event_data=timeline_data.event_data
            )
            
            self.db.add(timeline_event)
            self.db.commit()
            self.db.refresh(timeline_event)
            
            logger.info(f"Added timeline event for patient {timeline_data.patient_id}: {timeline_data.event_title}")
            return timeline_event
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding timeline event: {str(e)}")
            raise
    
    def get_patient_timeline(self, patient_id: str, limit: int = 100) -> List[PatientTimeline]:
        """Get patient timeline events."""
        return (self.db.query(PatientTimeline)
                .filter(PatientTimeline.patient_id == patient_id)
                .order_by(desc(PatientTimeline.event_date))
                .limit(limit)
                .all())
    
    # Comprehensive History
    def get_comprehensive_history(self, patient_id: str) -> Optional[ComprehensivePatientHistory]:
        """Get complete patient history for Q&A interface."""
        try:
            # Get patient
            patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                return None
            
            # Get visits
            visits = self.get_patient_visits(patient_id)
            
            # Get activities
            activities = self.get_patient_activities(patient_id)
            
            # Get timeline
            timeline = self.get_patient_timeline(patient_id)
            
            # Get medical records
            medical_records = (self.db.query(MedicalRecord)
                             .filter(MedicalRecord.patient_id == patient_id)
                             .order_by(desc(MedicalRecord.admission_date))
                             .all())
            
            # Get discharge notes
            discharge_notes = (self.db.query(DischargeNote)
                             .filter(DischargeNote.patient_id == patient_id)
                             .order_by(desc(DischargeNote.discharge_date))
                             .all())
            
            # Calculate statistics
            total_visits = len(visits)
            total_days_in_hospital = 0
            last_visit_date = None
            
            for visit in visits:
                if visit.discharge_date and visit.admission_date:
                    days = (visit.discharge_date - visit.admission_date).days
                    total_days_in_hospital += max(days, 1)  # At least 1 day
                
                if not last_visit_date or visit.admission_date > last_visit_date:
                    last_visit_date = visit.admission_date
            
            # Determine current status
            current_status = "outpatient"
            for visit in visits:
                if visit.status == "active":
                    current_status = "inpatient"
                    break
            
            # Convert to response models
            visit_responses = [PatientVisitResponse.from_orm(visit) for visit in visits]
            activity_responses = [PatientActivityResponse.from_orm(activity) for activity in activities]
            timeline_responses = [PatientTimelineResponse.from_orm(event) for event in timeline]
            
            # Convert patient to dict
            patient_dict = {
                "id": patient.id,
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth,
                "gender": patient.gender,
                "phone": patient.phone,
                "email": patient.email,
                "address": patient.address,
                "emergency_contact": patient.emergency_contact,
                "medical_history": patient.medical_history,
                "allergies": patient.allergies,
                "current_medications": patient.current_medications,
                "created_at": patient.created_at,
                "updated_at": patient.updated_at
            }
            
            # Convert medical records and discharge notes to dicts
            medical_records_dict = []
            for record in medical_records:
                medical_records_dict.append({
                    "id": record.id,
                    "patient_id": record.patient_id,
                    "admission_date": record.admission_date,
                    "discharge_date": record.discharge_date,
                    "primary_diagnosis": record.primary_diagnosis,
                    "secondary_diagnoses": record.secondary_diagnoses,
                    "procedures_performed": record.procedures_performed,
                    "treatment_summary": record.treatment_summary,
                    "physician_notes": record.physician_notes,
                    "nursing_notes": record.nursing_notes,
                    "lab_results": record.lab_results,
                    "vital_signs": record.vital_signs,
                    "severity_level": record.severity_level,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at
                })
            
            discharge_notes_dict = []
            for note in discharge_notes:
                discharge_notes_dict.append({
                    "id": note.id,
                    "patient_id": note.patient_id,
                    "medical_record_id": note.medical_record_id,
                    "discharge_summary": note.discharge_summary,
                    "medications_at_discharge": note.medications_at_discharge,
                    "follow_up_instructions": note.follow_up_instructions,
                    "activity_restrictions": note.activity_restrictions,
                    "diet_instructions": note.diet_instructions,
                    "warning_signs": note.warning_signs,
                    "discharge_physician": note.discharge_physician,
                    "discharge_date": note.discharge_date,
                    "created_at": note.created_at
                })
            
            return ComprehensivePatientHistory(
                patient=patient_dict,
                visits=visit_responses,
                activities=activity_responses,
                timeline=timeline_responses,
                medical_records=medical_records_dict,
                discharge_notes=discharge_notes_dict,
                total_visits=total_visits,
                total_days_in_hospital=total_days_in_hospital,
                last_visit_date=last_visit_date,
                current_status=current_status
            )
            
        except Exception as e:
            logger.error(f"Error getting comprehensive history: {str(e)}")
            raise
    
    # Automatic activity logging helpers
    def log_medication_change(self, patient_id: str, action: str, medication_name: str, performed_by: str = None):
        """Log medication changes."""
        activity_type = ActivityType.MEDICATION_ADDED if action == "added" else ActivityType.MEDICATION_REMOVED
        self.log_activity(PatientActivityCreate(
            patient_id=patient_id,
            activity_type=activity_type,
            description=f"Medication {action}: {medication_name}",
            details={"medication": medication_name, "action": action},
            performed_by=performed_by
        ))
    
    def log_diagnosis_update(self, patient_id: str, diagnosis: str, performed_by: str = None):
        """Log diagnosis updates."""
        self.log_activity(PatientActivityCreate(
            patient_id=patient_id,
            activity_type=ActivityType.DIAGNOSIS_UPDATED,
            description=f"Diagnosis updated: {diagnosis}",
            details={"diagnosis": diagnosis},
            performed_by=performed_by
        ))
    
    def log_procedure(self, patient_id: str, procedure: str, performed_by: str = None):
        """Log procedures performed."""
        self.log_activity(PatientActivityCreate(
            patient_id=patient_id,
            activity_type=ActivityType.PROCEDURE_PERFORMED,
            description=f"Procedure performed: {procedure}",
            details={"procedure": procedure},
            performed_by=performed_by
        ))
    
    def log_instruction_generation(self, patient_id: str, instruction_type: str, performed_by: str = None):
        """Log when discharge instructions are generated."""
        self.log_activity(PatientActivityCreate(
            patient_id=patient_id,
            activity_type=ActivityType.INSTRUCTION_GENERATED,
            description=f"Discharge instructions generated: {instruction_type}",
            details={"instruction_type": instruction_type},
            performed_by=performed_by
        ))
    
    def log_question_asked(self, patient_id: str, question: str, performed_by: str = None):
        """Log when questions are asked about the patient."""
        self.log_activity(PatientActivityCreate(
            patient_id=patient_id,
            activity_type=ActivityType.QUESTION_ASKED,
            description="Question asked about patient care",
            details={"question_preview": question[:100] + "..." if len(question) > 100 else question},
            performed_by=performed_by
        ))
