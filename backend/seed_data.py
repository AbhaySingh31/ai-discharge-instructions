#!/usr/bin/env python3
"""
Data seeding script for AI Discharge Instructions application.
Creates 100 mock patients with realistic medical data.
"""

import os
import sys
from datetime import datetime, timedelta
import random
from faker import Faker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import SessionLocal, create_tables
from app.models.patient import Patient, MedicalRecord, DischargeNote

fake = Faker()

# Medical data for realistic mock generation
MEDICAL_CONDITIONS = [
    "Hypertension", "Type 2 Diabetes", "Coronary Artery Disease", "Asthma", "COPD",
    "Pneumonia", "Acute Myocardial Infarction", "Stroke", "Appendicitis", "Cholecystitis",
    "Gastroenteritis", "Urinary Tract Infection", "Cellulitis", "Fracture", "Migraine",
    "Depression", "Anxiety", "Chronic Kidney Disease", "Heart Failure", "Atrial Fibrillation"
]

MEDICATIONS = [
    {"name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "route": "Oral"},
    {"name": "Metformin", "dosage": "500mg", "frequency": "Twice daily", "route": "Oral"},
    {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily", "route": "Oral"},
    {"name": "Albuterol", "dosage": "90mcg", "frequency": "As needed", "route": "Inhaled"},
    {"name": "Omeprazole", "dosage": "20mg", "frequency": "Once daily", "route": "Oral"},
    {"name": "Aspirin", "dosage": "81mg", "frequency": "Once daily", "route": "Oral"},
    {"name": "Furosemide", "dosage": "40mg", "frequency": "Once daily", "route": "Oral"},
    {"name": "Warfarin", "dosage": "5mg", "frequency": "Once daily", "route": "Oral"},
    {"name": "Insulin", "dosage": "10 units", "frequency": "Before meals", "route": "Subcutaneous"},
    {"name": "Prednisone", "dosage": "20mg", "frequency": "Once daily", "route": "Oral"}
]

ALLERGIES = [
    {"allergen": "Penicillin", "reaction": "Rash", "severity": "moderate"},
    {"allergen": "Shellfish", "reaction": "Anaphylaxis", "severity": "high"},
    {"allergen": "Latex", "reaction": "Contact dermatitis", "severity": "low"},
    {"allergen": "Sulfa drugs", "reaction": "Hives", "severity": "moderate"},
    {"allergen": "Peanuts", "reaction": "Swelling", "severity": "high"},
    {"allergen": "Iodine", "reaction": "Rash", "severity": "moderate"},
    {"allergen": "Codeine", "reaction": "Nausea", "severity": "low"},
    {"allergen": "Aspirin", "reaction": "GI upset", "severity": "moderate"}
]

PROCEDURES = [
    "Cardiac catheterization", "Appendectomy", "Cholecystectomy", "Endoscopy",
    "Colonoscopy", "CT scan", "MRI", "X-ray", "Blood transfusion", "IV therapy",
    "Oxygen therapy", "Physical therapy", "Wound care", "Medication administration"
]

def generate_patient_data(patient_num):
    """Generate realistic patient data."""
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Generate patient ID in format P000001, P000002, etc.
    patient_id = f"P{patient_num:06d}"
    
    # Random birth date between 18 and 90 years ago
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)
    
    gender = random.choice(["male", "female", "other"])
    
    # Emergency contact
    emergency_contact = {
        "name": fake.name(),
        "relationship": random.choice(["Spouse", "Parent", "Sibling", "Child", "Friend"]),
        "phone": fake.phone_number(),
        "email": fake.email()
    }
    
    # Medical history (1-4 conditions)
    medical_history = random.sample(MEDICAL_CONDITIONS, random.randint(1, 4))
    
    # Allergies (0-3 allergies)
    num_allergies = random.randint(0, 3)
    allergies = random.sample(ALLERGIES, num_allergies) if num_allergies > 0 else []
    
    # Current medications (1-5 medications)
    num_meds = random.randint(1, 5)
    current_medications = random.sample(MEDICATIONS, num_meds)
    
    return {
        "patient_id": patient_id,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": birth_date,
        "gender": gender,
        "phone": fake.phone_number(),
        "email": fake.email(),
        "emergency_contact": emergency_contact,
        "medical_history": medical_history,
        "allergies": allergies,
        "current_medications": current_medications
    }

def generate_medical_record_data(patient_id):
    """Generate realistic medical record data."""
    admission_date = fake.date_time_between(start_date='-30d', end_date='now')
    discharge_date = admission_date + timedelta(days=random.randint(1, 14))
    
    primary_diagnosis = random.choice(MEDICAL_CONDITIONS)
    secondary_diagnoses = random.sample(
        [c for c in MEDICAL_CONDITIONS if c != primary_diagnosis], 
        random.randint(0, 2)
    )
    
    procedures_performed = random.sample(PROCEDURES, random.randint(1, 4))
    
    # Generate vital signs
    vital_signs = [{
        "temperature": round(random.uniform(97.0, 101.5), 1),
        "blood_pressure_systolic": random.randint(110, 180),
        "blood_pressure_diastolic": random.randint(60, 110),
        "heart_rate": random.randint(60, 120),
        "respiratory_rate": random.randint(12, 24),
        "oxygen_saturation": round(random.uniform(92.0, 100.0), 1),
        "recorded_at": admission_date.isoformat()
    }]
    
    # Generate lab results
    lab_results = [
        {
            "test_name": "Complete Blood Count",
            "value": f"{random.randint(4, 11)}.{random.randint(0, 9)}",
            "unit": "K/uL",
            "reference_range": "4.5-11.0",
            "status": random.choice(["normal", "abnormal"]),
            "recorded_at": admission_date.isoformat()
        },
        {
            "test_name": "Blood Glucose",
            "value": str(random.randint(70, 250)),
            "unit": "mg/dL",
            "reference_range": "70-100",
            "status": random.choice(["normal", "abnormal"]),
            "recorded_at": admission_date.isoformat()
        }
    ]
    
    return {
        "patient_id": patient_id,
        "admission_date": admission_date,
        "discharge_date": discharge_date,
        "primary_diagnosis": primary_diagnosis,
        "secondary_diagnoses": secondary_diagnoses,
        "procedures_performed": procedures_performed,
        "treatment_summary": f"Patient admitted with {primary_diagnosis}. Received appropriate treatment and monitoring. Condition improved with medication and supportive care.",
        "physician_notes": f"Patient responded well to treatment. Vital signs stable. Ready for discharge with follow-up care.",
        "nursing_notes": "Patient cooperative with care. No complications noted. Discharge teaching completed.",
        "lab_results": lab_results,
        "vital_signs": vital_signs,
        "severity_level": random.choice(["low", "moderate", "high"])
    }

def generate_discharge_note_data(patient_id, medical_record_id, discharge_date):
    """Generate realistic discharge note data."""
    
    # Discharge medications (2-6 medications)
    num_discharge_meds = random.randint(2, 6)
    medications_at_discharge = random.sample(MEDICATIONS, num_discharge_meds)
    
    discharge_physician = f"Dr. {fake.last_name()}"
    
    return {
        "patient_id": patient_id,
        "medical_record_id": medical_record_id,
        "discharge_summary": f"Patient admitted with acute condition and received comprehensive care. Condition stabilized with appropriate treatment. Patient educated on discharge instructions and follow-up care.",
        "medications_at_discharge": medications_at_discharge,
        "follow_up_instructions": "Follow up with primary care physician in 1-2 weeks. Return to emergency department if symptoms worsen.",
        "activity_restrictions": "Light activity for 1 week. Gradually increase activity as tolerated. No heavy lifting over 10 pounds.",
        "diet_instructions": "Regular diet as tolerated. Increase fluid intake. Limit sodium intake.",
        "warning_signs": "Return immediately if experiencing severe pain, difficulty breathing, fever over 101°F, or any concerning symptoms.",
        "discharge_physician": discharge_physician,
        "discharge_date": discharge_date
    }

def seed_database():
    """Seed the database with mock patient data."""
    print("Creating database tables...")
    create_tables()
    
    db = SessionLocal()
    
    try:
        print("Seeding database with 100 patients...")
        
        for i in range(1, 101):
            print(f"Creating patient {i}/100...")
            
            # Generate patient data
            patient_data = generate_patient_data(i)
            
            # Create patient
            patient = Patient(**patient_data)
            db.add(patient)
            db.flush()  # Get the patient ID
            
            # Generate 1-3 medical records per patient
            num_records = random.randint(1, 3)
            
            for j in range(num_records):
                # Generate medical record
                record_data = generate_medical_record_data(patient_data["patient_id"])
                medical_record = MedicalRecord(**record_data)
                db.add(medical_record)
                db.flush()  # Get the medical record ID
                
                # Generate discharge note
                discharge_data = generate_discharge_note_data(
                    patient_data["patient_id"], 
                    medical_record.id, 
                    record_data["discharge_date"]
                )
                discharge_note = DischargeNote(**discharge_data)
                db.add(discharge_note)
        
        # Commit all changes
        db.commit()
        print("✅ Successfully seeded database with 100 patients!")
        
        # Print some statistics
        patient_count = db.query(Patient).count()
        record_count = db.query(MedicalRecord).count()
        note_count = db.query(DischargeNote).count()
        
        print(f"📊 Database Statistics:")
        print(f"   - Patients: {patient_count}")
        print(f"   - Medical Records: {record_count}")
        print(f"   - Discharge Notes: {note_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
