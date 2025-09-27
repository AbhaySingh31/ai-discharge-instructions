#!/usr/bin/env python3
"""
Test the fixed Q&A endpoints.
"""

import requests
import json

def test_comprehensive_history():
    """Test the comprehensive history endpoint."""
    try:
        response = requests.get('http://localhost:8000/api/v1/patients/P000001/comprehensive-history', timeout=10)
        print(f'Comprehensive History Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Comprehensive history endpoint working!')
            patient = data['patient']
            print(f'Patient: {patient["first_name"]} {patient["last_name"]}')
            print(f'Medical Records: {len(data["medical_records"])}')
            print(f'Current Medications: {len(patient["current_medications"])}')
            return True
        else:
            print(f'❌ Error: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False

def test_enhanced_qa():
    """Test the enhanced Q&A endpoint."""
    try:
        qa_data = {'question': 'What medications should I take?'}
        response = requests.post('http://localhost:8000/api/v1/ask-question-enhanced/P000001', 
                               json=qa_data, timeout=15)
        print(f'Enhanced Q&A Status: {response.status_code}')
        
        if response.status_code == 200:
            qa_result = response.json()
            print('✅ Enhanced Q&A endpoint working!')
            print(f'Question: {qa_result["question"]}')
            print(f'Answer preview: {qa_result["answer"][:100]}...')
            print(f'Confidence: {qa_result.get("confidence", "N/A")}')
            print(f'Safety flags: {qa_result.get("safety_flags", [])}')
            return True
        else:
            print(f'❌ Q&A Error: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False

if __name__ == "__main__":
    print("🧪 Testing Fixed Q&A System")
    print("=" * 50)
    
    history_working = test_comprehensive_history()
    print()
    qa_working = test_enhanced_qa()
    
    print("\n" + "=" * 50)
    if history_working and qa_working:
        print("🎉 Q&A System is now working!")
        print("\n✅ You can now access:")
        print("1. Patient Q&A interface at /patients/P000001/qa")
        print("2. Ask questions and get AI responses")
        print("3. View comprehensive patient information")
    else:
        print("❌ Some endpoints still need work")
        if history_working:
            print("✅ Patient data loading works")
        if qa_working:
            print("✅ Q&A system works")
