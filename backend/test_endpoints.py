#!/usr/bin/env python3
"""
Test script to verify all endpoints are working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_patients_list():
    """Test getting list of patients."""
    try:
        response = requests.get(f"{BASE_URL}/patients/")
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Patients endpoint working: {len(patients)} patients found")
            return patients[0] if patients else None
        else:
            print(f"❌ Patients endpoint failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Patients endpoint error: {e}")
        return None

def test_patient_detail(patient_id):
    """Test getting patient details."""
    try:
        response = requests.get(f"{BASE_URL}/patients/{patient_id}")
        if response.status_code == 200:
            patient = response.json()
            print(f"✅ Patient detail working: {patient['first_name']} {patient['last_name']}")
            return patient
        else:
            print(f"❌ Patient detail failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Patient detail error: {e}")
        return None

def test_medical_records(patient_id):
    """Test getting medical records."""
    try:
        response = requests.get(f"{BASE_URL}/medical-records/{patient_id}")
        if response.status_code == 200:
            records = response.json()
            print(f"✅ Medical records working: {len(records)} records found")
            return records[0] if records else None
        else:
            print(f"❌ Medical records failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Medical records error: {e}")
        return None

def test_quick_discharge_summary(patient_id, medical_record_id):
    """Test quick discharge summary generation."""
    try:
        response = requests.post(f"{BASE_URL}/generate-quick-discharge/{patient_id}?medical_record_id={medical_record_id}")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Quick discharge summary working: Generated {len(summary['discharge_summary'])} characters")
            return True
        else:
            print(f"❌ Quick discharge summary failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Quick discharge summary error: {e}")
        return False

def test_patient_search():
    """Test patient search functionality."""
    try:
        response = requests.get(f"{BASE_URL}/patients/search/P000001")
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Patient search working: {len(results)} results found")
            return True
        else:
            print(f"❌ Patient search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Patient search error: {e}")
        return False

def main():
    print("🧪 Testing AI Discharge Instructions API Endpoints")
    print("=" * 50)
    
    # Test 1: List patients
    patients = test_patients_list()
    if not patients:
        print("❌ Cannot continue tests without patient data")
        return
    
    patient_id = patients['patient_id']
    print(f"Using test patient: {patient_id}")
    
    # Test 2: Patient details
    patient = test_patient_detail(patient_id)
    if not patient:
        return
    
    # Test 3: Medical records
    medical_record = test_medical_records(patient_id)
    if not medical_record:
        return
    
    # Test 4: Quick discharge summary
    test_quick_discharge_summary(patient_id, medical_record['id'])
    
    # Test 5: Patient search
    test_patient_search()
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")

if __name__ == "__main__":
    main()
