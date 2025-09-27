#!/usr/bin/env python3
"""
Migration script to populate patient history tables with sample data.
"""

import os
import sys
from datetime import datetime, timedelta
import random
from faker import Faker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import SessionLocal, create_tables
from app.models.patient import Patient, MedicalRecord
from app.models.patient_history import (
    PatientActivity, PatientVisit, PatientTimeline,
    ActivityType
)
from app.services.patient_history_service import PatientHistoryService

fake = Faker()

def create_sample_visits_and_activities():
    """Create sample visits and activities for existing patients."""
    print("Creating sample patient visits and activities...")
    
    db = SessionLocal()
    history_service = PatientHistoryService(db)
    
    try:
        # Get all existing patients
        patients = db.query(Patient).all()
        print(f"Found {len(patients)} patients to process...")
        
        for i, patient in enumerate(patients[:20]):  # Process first 20 patients for demo
            print(f"Processing patient {i+1}/20: {patient.patient_id}")
            
            # Create 1-3 visits per patient
            num_visits = random.randint(1, 3)
            
            for visit_num in range(1, num_visits + 1):
                # Create visit
                admission_date = fake.date_time_between(start_date='-2y', end_date='now')
                discharge_date = admission_date + timedelta(days=random.randint(1, 14))
                
                visit_number = f"{patient.patient_id}-V{visit_num:03d}"
                visit_type = random.choice(['emergency', 'scheduled', 'follow_up'])
                department = random.choice(['cardiology', 'surgery', 'internal_medicine', 'emergency', 'orthopedics'])
                
                visit = PatientVisit(
                    patient_id=patient.patient_id,
                    visit_number=visit_number,
                    admission_date=admission_date,
                    discharge_date=discharge_date,
                    visit_type=visit_type,
                    department=department,
                    attending_physician=fake.name(),
                    status='discharged',
                    chief_complaint=fake.sentence(nb_words=6),
                    visit_summary=fake.text(max_nb_chars=200),
                    discharge_disposition='home'
                )
                
                db.add(visit)
                db.flush()  # Get the visit ID
                
                # Create activities for this visit
                activities = [
                    {
                        'type': ActivityType.ADMISSION,
                        'description': f'Patient admitted to {department} for {visit_type} visit',
                        'timestamp': admission_date,
                        'details': {'department': department, 'visit_type': visit_type}
                    },
                    {
                        'type': ActivityType.DIAGNOSIS_UPDATED,
                        'description': f'Primary diagnosis: {fake.word().title()} condition',
                        'timestamp': admission_date + timedelta(hours=2),
                        'details': {'diagnosis': fake.word().title()}
                    },
                    {
                        'type': ActivityType.MEDICATION_ADDED,
                        'description': f'Medication added: {fake.word().title()}',
                        'timestamp': admission_date + timedelta(hours=4),
                        'details': {'medication': fake.word().title()}
                    },
                    {
                        'type': ActivityType.PROCEDURE_PERFORMED,
                        'description': f'Procedure: {fake.word().title()} examination',
                        'timestamp': admission_date + timedelta(days=1),
                        'details': {'procedure': fake.word().title()}
                    },
                    {
                        'type': ActivityType.DISCHARGE,
                        'description': f'Patient discharged to {visit.discharge_disposition}',
                        'timestamp': discharge_date,
                        'details': {'disposition': visit.discharge_disposition}
                    }
                ]
                
                for activity_data in activities:
                    activity = PatientActivity(
                        patient_id=patient.patient_id,
                        activity_type=activity_data['type'].value,
                        description=activity_data['description'],
                        details=activity_data['details'],
                        performed_by=visit.attending_physician,
                        timestamp=activity_data['timestamp']
                    )
                    db.add(activity)
                
                # Create timeline events
                timeline_events = [
                    {
                        'event_type': 'admission',
                        'event_title': f'Admitted to {department}',
                        'event_description': visit.chief_complaint,
                        'event_date': admission_date,
                        'severity': 'medium',
                        'category': 'administrative'
                    },
                    {
                        'event_type': 'diagnosis',
                        'event_title': 'Primary diagnosis established',
                        'event_description': f'Diagnosed with {fake.word().title()} condition',
                        'event_date': admission_date + timedelta(hours=2),
                        'severity': 'high',
                        'category': 'clinical'
                    },
                    {
                        'event_type': 'treatment',
                        'event_title': 'Treatment initiated',
                        'event_description': f'Started {fake.word().title()} therapy',
                        'event_date': admission_date + timedelta(hours=6),
                        'severity': 'medium',
                        'category': 'clinical'
                    },
                    {
                        'event_type': 'discharge',
                        'event_title': 'Patient discharged',
                        'event_description': f'Discharged to {visit.discharge_disposition} in stable condition',
                        'event_date': discharge_date,
                        'severity': 'low',
                        'category': 'administrative'
                    }
                ]
                
                for timeline_data in timeline_events:
                    timeline_event = PatientTimeline(
                        patient_id=patient.patient_id,
                        visit_id=visit.id,
                        event_type=timeline_data['event_type'],
                        event_title=timeline_data['event_title'],
                        event_description=timeline_data['event_description'],
                        event_date=timeline_data['event_date'],
                        severity=timeline_data['severity'],
                        category=timeline_data['category'],
                        performed_by=visit.attending_physician,
                        location=department
                    )
                    db.add(timeline_event)
        
        # Commit all changes
        db.commit()
        print("✅ Successfully created sample visits and activities!")
        
        # Print statistics
        visit_count = db.query(PatientVisit).count()
        activity_count = db.query(PatientActivity).count()
        timeline_count = db.query(PatientTimeline).count()
        
        print(f"📊 History Data Statistics:")
        print(f"   - Patient Visits: {visit_count}")
        print(f"   - Patient Activities: {activity_count}")
        print(f"   - Timeline Events: {timeline_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating history data: {str(e)}")
        raise
    finally:
        db.close()

def main():
    print("🏥 AI Discharge Instructions - Patient History Migration")
    print("=" * 60)
    
    # Create tables first
    print("Creating database tables...")
    create_tables()
    
    # Create sample data
    create_sample_visits_and_activities()
    
    print("\n" + "=" * 60)
    print("🎉 Migration completed successfully!")
    print("\nYou can now:")
    print("1. View comprehensive patient histories")
    print("2. Use the enhanced AI Q&A system")
    print("3. Track detailed patient activities and timelines")

if __name__ == "__main__":
    main()
