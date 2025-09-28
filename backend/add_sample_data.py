#!/usr/bin/env python3
"""
Quick script to add sample patient data to the deployed Railway database.
Run this locally to populate the Railway database with test data.
"""

import requests
import json

# Railway API base URL
BASE_URL = "https://web-production-f3389.up.railway.app/api/v1"

def add_sample_patients():
    """Add sample patients to the database."""
    
    sample_patients = [
        {
            "patient_id": "P000001",
            "first_name": "Anthony",
            "last_name": "Griffin",
            "date_of_birth": "1985-03-15",
            "gender": "Male",
            "phone": "555-0101",
            "email": "anthony.griffin@email.com",
            "emergency_contact": "Sarah Griffin - Wife - 555-0102",
            "medical_history": ["Hypertension", "Type 2 Diabetes"],
            "allergies": ["Penicillin", "Shellfish"],
            "current_medications": [
                {
                    "name": "Lisinopril",
                    "dosage": "10mg",
                    "frequency": "Once daily",
                    "route": "Oral"
                },
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "Twice daily",
                    "route": "Oral"
                }
            ]
        },
        {
            "patient_id": "P000002",
            "first_name": "Maria",
            "last_name": "Rodriguez",
            "date_of_birth": "1978-07-22",
            "gender": "Female",
            "phone": "555-0201",
            "email": "maria.rodriguez@email.com",
            "emergency_contact": "Carlos Rodriguez - Husband - 555-0202",
            "medical_history": ["Asthma", "Seasonal Allergies"],
            "allergies": ["Latex", "Pollen"],
            "current_medications": [
                {
                    "name": "Albuterol",
                    "dosage": "90mcg",
                    "frequency": "As needed",
                    "route": "Inhaled"
                }
            ]
        },
        {
            "patient_id": "P000003",
            "first_name": "James",
            "last_name": "Wilson",
            "date_of_birth": "1965-11-08",
            "gender": "Male",
            "phone": "555-0301",
            "email": "james.wilson@email.com",
            "emergency_contact": "Linda Wilson - Wife - 555-0302",
            "medical_history": ["Heart Disease", "High Cholesterol"],
            "allergies": ["Aspirin"],
            "current_medications": [
                {
                    "name": "Atorvastatin",
                    "dosage": "20mg",
                    "frequency": "Once daily",
                    "route": "Oral"
                }
            ]
        }
    ]
    
    print("🏥 Adding sample patients to Railway database...")
    
    for patient in sample_patients:
        try:
            response = requests.post(f"{BASE_URL}/patients", json=patient)
            if response.status_code == 201:
                print(f"✅ Added patient: {patient['first_name']} {patient['last_name']} ({patient['patient_id']})")
            else:
                print(f"❌ Failed to add patient {patient['patient_id']}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error adding patient {patient['patient_id']}: {str(e)}")
    
    print("\n🎯 Testing API endpoints...")
    
    # Test patients list
    try:
        response = requests.get(f"{BASE_URL}/patients")
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Found {len(patients)} patients in database")
        else:
            print(f"❌ Failed to get patients: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting patients: {str(e)}")

if __name__ == "__main__":
    add_sample_patients()
