#!/usr/bin/env python3
"""
Simple migration to add new tables and sample data.
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
import random
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_history_tables():
    """Create the new history tables directly in SQLite."""
    db_path = "discharge_instructions.db"
    
    print("Creating patient history tables...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create patient_activities table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            details TEXT,
            performed_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        """)
        
        # Create patient_visits table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            visit_number TEXT NOT NULL UNIQUE,
            admission_date DATETIME NOT NULL,
            discharge_date DATETIME,
            visit_type TEXT NOT NULL,
            department TEXT,
            attending_physician TEXT,
            status TEXT DEFAULT 'active',
            chief_complaint TEXT,
            visit_summary TEXT,
            discharge_disposition TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        """)
        
        # Create patient_timeline table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            visit_id INTEGER,
            event_type TEXT NOT NULL,
            event_title TEXT NOT NULL,
            event_description TEXT,
            event_date DATETIME NOT NULL,
            severity TEXT,
            category TEXT,
            performed_by TEXT,
            location TEXT,
            event_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (visit_id) REFERENCES patient_visits (id)
        )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_patient_id ON patient_activities (patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON patient_activities (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_visits_patient_id ON patient_visits (patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_patient_id ON patient_timeline (patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_event_date ON patient_timeline (event_date)")
        
        conn.commit()
        print("✅ History tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {str(e)}")
        raise
    finally:
        conn.close()

def add_sample_history_data():
    """Add sample history data for first 10 patients."""
    db_path = "discharge_instructions.db"
    
    print("Adding sample history data...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get first 10 patients
        cursor.execute("SELECT patient_id, first_name, last_name FROM patients LIMIT 10")
        patients = cursor.fetchall()
        
        print(f"Adding history for {len(patients)} patients...")
        
        for i, (patient_id, first_name, last_name) in enumerate(patients):
            print(f"Processing {patient_id} - {first_name} {last_name}")
            
            # Create 1-2 visits per patient
            num_visits = random.randint(1, 2)
            
            for visit_num in range(1, num_visits + 1):
                visit_number = f"{patient_id}-V{visit_num:03d}"
                
                # Generate visit dates
                admission_date = datetime.now() - timedelta(days=random.randint(30, 365))
                discharge_date = admission_date + timedelta(days=random.randint(1, 7))
                
                visit_type = random.choice(['emergency', 'scheduled', 'follow_up'])
                department = random.choice(['cardiology', 'surgery', 'internal_medicine', 'emergency'])
                physician = f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Davis'])}"
                
                # Insert visit
                cursor.execute("""
                INSERT INTO patient_visits 
                (patient_id, visit_number, admission_date, discharge_date, visit_type, 
                 department, attending_physician, status, chief_complaint, visit_summary, 
                 discharge_disposition)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_id, visit_number, admission_date, discharge_date, visit_type,
                    department, physician, 'discharged', 
                    f'Patient presented with {random.choice(["chest pain", "shortness of breath", "abdominal pain", "headache"])}',
                    f'Patient was treated for {random.choice(["acute condition", "chronic condition", "routine care"])} and responded well to treatment.',
                    'home'
                ))
                
                visit_id = cursor.lastrowid
                
                # Add activities for this visit
                activities = [
                    ('admission', f'Patient admitted to {department}', admission_date, physician),
                    ('diagnosis_updated', f'Primary diagnosis established', admission_date + timedelta(hours=2), physician),
                    ('medication_added', f'Medication therapy initiated', admission_date + timedelta(hours=4), physician),
                    ('procedure_performed', f'Diagnostic procedure completed', admission_date + timedelta(days=1), physician),
                    ('discharge', f'Patient discharged home', discharge_date, physician)
                ]
                
                for activity_type, description, timestamp, performed_by in activities:
                    cursor.execute("""
                    INSERT INTO patient_activities 
                    (patient_id, activity_type, description, performed_by, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """, (patient_id, activity_type, description, performed_by, timestamp))
                
                # Add timeline events
                timeline_events = [
                    ('admission', f'Admitted to {department}', f'Patient admitted for {visit_type} care', admission_date, 'medium', 'administrative'),
                    ('diagnosis', 'Diagnosis established', 'Primary diagnosis confirmed', admission_date + timedelta(hours=2), 'high', 'clinical'),
                    ('treatment', 'Treatment started', 'Therapeutic intervention initiated', admission_date + timedelta(hours=6), 'medium', 'clinical'),
                    ('discharge', 'Patient discharged', 'Discharged in stable condition', discharge_date, 'low', 'administrative')
                ]
                
                for event_type, title, description, event_date, severity, category in timeline_events:
                    cursor.execute("""
                    INSERT INTO patient_timeline 
                    (patient_id, visit_id, event_type, event_title, event_description, 
                     event_date, severity, category, performed_by, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (patient_id, visit_id, event_type, title, description, 
                          event_date, severity, category, physician, department))
        
        conn.commit()
        print("✅ Sample history data added successfully!")
        
        # Print statistics
        cursor.execute("SELECT COUNT(*) FROM patient_visits")
        visit_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patient_activities")
        activity_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patient_timeline")
        timeline_count = cursor.fetchone()[0]
        
        print(f"📊 History Data Statistics:")
        print(f"   - Patient Visits: {visit_count}")
        print(f"   - Patient Activities: {activity_count}")
        print(f"   - Timeline Events: {timeline_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding sample data: {str(e)}")
        raise
    finally:
        conn.close()

def main():
    print("🏥 AI Discharge Instructions - Simple History Migration")
    print("=" * 60)
    
    # Create tables
    create_history_tables()
    
    # Add sample data
    add_sample_history_data()
    
    print("\n" + "=" * 60)
    print("🎉 Migration completed successfully!")
    print("\nNew features available:")
    print("1. 📊 Comprehensive patient histories")
    print("2. 🤖 Enhanced AI Q&A with PII protection")
    print("3. 📝 Detailed activity tracking")
    print("4. 📅 Patient timeline visualization")
    print("\nYou can now visit /patients/{patient_id}/qa to try the new Q&A interface!")

if __name__ == "__main__":
    main()
