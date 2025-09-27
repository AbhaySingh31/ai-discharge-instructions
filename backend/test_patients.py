#!/usr/bin/env python3
"""
Test patients endpoint after fixing database issues.
"""

import requests

def test_patients_endpoint():
    """Test the patients endpoint."""
    try:
        response = requests.get('http://localhost:8000/api/v1/patients/', timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Patients endpoint working: {len(data)} patients')
            if data:
                first_patient = data[0]
                print(f'First patient: {first_patient["patient_id"]} - {first_patient["first_name"]} {first_patient["last_name"]}')
            return True
        else:
            print(f'❌ Error: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False

if __name__ == "__main__":
    print("🧪 Testing Patients Endpoint")
    print("=" * 40)
    
    if test_patients_endpoint():
        print("\n✅ Frontend should now load patients successfully!")
        print("🚀 You can now access the enhanced Q&A system!")
    else:
        print("\n❌ Still having issues with the patients endpoint")
