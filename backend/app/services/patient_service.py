from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models.patient import (
    Patient, MedicalRecord, DischargeNote,
    PatientCreate, MedicalRecordCreate, DischargeNoteCreate
)

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, db: Session):
        self.db = db

    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient record."""
        try:
            # Check if patient already exists
            existing_patient = self.db.query(Patient).filter(
                Patient.patient_id == patient_data.patient_id
            ).first()
            
            if existing_patient:
                raise ValueError(f"Patient with ID {patient_data.patient_id} already exists")
            
            # Convert Pydantic model to dict and handle nested objects
            patient_dict = patient_data.model_dump()
            
            # Convert emergency_contact to dict if it exists
            if patient_dict.get('emergency_contact'):
                patient_dict['emergency_contact'] = patient_dict['emergency_contact']
            
            # Convert allergies list to dict format
            if patient_dict.get('allergies'):
                patient_dict['allergies'] = [
                    allergy.model_dump() if hasattr(allergy, 'model_dump') else allergy
                    for allergy in patient_dict['allergies']
                ]
            
            # Convert medications list to dict format
            if patient_dict.get('current_medications'):
                patient_dict['current_medications'] = [
                    med.model_dump() if hasattr(med, 'model_dump') else med
                    for med in patient_dict['current_medications']
                ]
            
            db_patient = Patient(**patient_dict)
            self.db.add(db_patient)
            self.db.commit()
            self.db.refresh(db_patient)
            
            logger.info(f"Created patient: {patient_data.patient_id}")
            return db_patient
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating patient: {str(e)}")
            raise

    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by patient ID."""
        return self.db.query(Patient).filter(Patient.patient_id == patient_id).first()

    def get_patients(self, skip: int = 0, limit: int = 1000) -> List[Patient]:
        """Get all patients with pagination."""
        return self.db.query(Patient).offset(skip).limit(limit).all()

    def update_patient(self, patient_id: str, patient_data: dict) -> Optional[Patient]:
        """Update patient information."""
        try:
            patient = self.get_patient_by_id(patient_id)
            if not patient:
                return None
            
            for key, value in patient_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            
            self.db.commit()
            self.db.refresh(patient)
            
            logger.info(f"Updated patient: {patient_id}")
            return patient
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating patient: {str(e)}")
            raise

    def create_medical_record(self, record_data: MedicalRecordCreate) -> MedicalRecord:
        """Create a new medical record."""
        try:
            # Verify patient exists
            patient = self.get_patient_by_id(record_data.patient_id)
            if not patient:
                raise ValueError(f"Patient with ID {record_data.patient_id} not found")
            
            # Convert Pydantic model to dict
            record_dict = record_data.model_dump()
            
            # Convert lab_results and vital_signs to proper format
            if record_dict.get('lab_results'):
                record_dict['lab_results'] = [
                    result.model_dump() if hasattr(result, 'model_dump') else result
                    for result in record_dict['lab_results']
                ]
            
            if record_dict.get('vital_signs'):
                record_dict['vital_signs'] = [
                    vital.model_dump() if hasattr(vital, 'model_dump') else vital
                    for vital in record_dict['vital_signs']
                ]
            
            db_record = MedicalRecord(**record_dict)
            self.db.add(db_record)
            self.db.commit()
            self.db.refresh(db_record)
            
            logger.info(f"Created medical record for patient: {record_data.patient_id}")
            return db_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating medical record: {str(e)}")
            raise

    def get_medical_record_by_id(self, record_id: int) -> Optional[MedicalRecord]:
        """Get medical record by ID."""
        return self.db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()

    def get_medical_records_by_patient(self, patient_id: str) -> List[MedicalRecord]:
        """Get all medical records for a patient."""
        return self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).order_by(MedicalRecord.admission_date.desc()).all()

    def create_discharge_note(self, note_data: DischargeNoteCreate) -> DischargeNote:
        """Create a new discharge note."""
        try:
            # Verify patient exists
            patient = self.get_patient_by_id(note_data.patient_id)
            if not patient:
                raise ValueError(f"Patient with ID {note_data.patient_id} not found")
            
            # Verify medical record exists
            medical_record = self.get_medical_record_by_id(note_data.medical_record_id)
            if not medical_record or medical_record.patient_id != note_data.patient_id:
                raise ValueError(f"Medical record {note_data.medical_record_id} not found for patient {note_data.patient_id}")
            
            # Convert Pydantic model to dict
            note_dict = note_data.model_dump()
            
            # Convert medications_at_discharge to proper format
            if note_dict.get('medications_at_discharge'):
                note_dict['medications_at_discharge'] = [
                    med.model_dump() if hasattr(med, 'model_dump') else med
                    for med in note_dict['medications_at_discharge']
                ]
            
            db_note = DischargeNote(**note_dict)
            self.db.add(db_note)
            self.db.commit()
            self.db.refresh(db_note)
            
            logger.info(f"Created discharge note for patient: {note_data.patient_id}")
            return db_note
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating discharge note: {str(e)}")
            raise

    def get_discharge_notes_by_patient(self, patient_id: str) -> List[DischargeNote]:
        """Get all discharge notes for a patient."""
        return self.db.query(DischargeNote).filter(
            DischargeNote.patient_id == patient_id
        ).order_by(DischargeNote.discharge_date.desc()).all()

    def get_discharge_notes_by_medical_record(self, medical_record_id: int) -> List[DischargeNote]:
        """Get discharge notes for a specific medical record."""
        return self.db.query(DischargeNote).filter(
            DischargeNote.medical_record_id == medical_record_id
        ).order_by(DischargeNote.discharge_date.desc()).all()

    def get_latest_discharge_note(self, patient_id: str) -> Optional[DischargeNote]:
        """Get the most recent discharge note for a patient."""
        return self.db.query(DischargeNote).filter(
            DischargeNote.patient_id == patient_id
        ).order_by(DischargeNote.discharge_date.desc()).first()

    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient and all associated records."""
        try:
            patient = self.get_patient_by_id(patient_id)
            if not patient:
                return False
            
            # Delete associated records first
            self.db.query(DischargeNote).filter(
                DischargeNote.patient_id == patient_id
            ).delete()
            
            self.db.query(MedicalRecord).filter(
                MedicalRecord.patient_id == patient_id
            ).delete()
            
            # Delete patient
            self.db.delete(patient)
            self.db.commit()
            
            logger.info(f"Deleted patient and all associated records: {patient_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting patient: {str(e)}")
            raise

    def search_patients(self, query: str) -> List[Patient]:
        """Search patients by name or patient ID."""
        return self.db.query(Patient).filter(
            (Patient.first_name.ilike(f"%{query}%")) |
            (Patient.last_name.ilike(f"%{query}%")) |
            (Patient.patient_id.ilike(f"%{query}%"))
        ).all()

    def get_patient_summary(self, patient_id: str) -> Optional[dict]:
        """Get a comprehensive summary of patient data."""
        try:
            patient = self.get_patient_by_id(patient_id)
            if not patient:
                return None
            
            medical_records = self.get_medical_records_by_patient(patient_id)
            discharge_notes = self.get_discharge_notes_by_patient(patient_id)
            
            return {
                "patient": patient,
                "medical_records": medical_records,
                "discharge_notes": discharge_notes,
                "total_admissions": len(medical_records),
                "latest_admission": medical_records[0] if medical_records else None,
                "latest_discharge": discharge_notes[0] if discharge_notes else None
            }
            
        except Exception as e:
            logger.error(f"Error getting patient summary: {str(e)}")
            raise
