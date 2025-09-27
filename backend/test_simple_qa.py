#!/usr/bin/env python3
"""
Test Q&A with simple patient data to verify it's working with actual patient information.
"""

import requests
import json

def test_medication_question():
    """Test asking about medications."""
    qa_data = {'question': 'What medications should I take and when?'}
    
    try:
        response = requests.post('http://localhost:8000/api/v1/ask-question-enhanced/P000001', 
                               json=qa_data, timeout=20)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ Q&A Response:')
            print(f'Question: {result["question"]}')
            print(f'Answer: {result["answer"]}')
            print(f'Confidence: {result.get("confidence", "N/A")}')
            
            # Check if response mentions specific medications or is generic
            answer = result["answer"].lower()
            if any(med in answer for med in ['prednisone', 'lisinopril', 'metformin', 'medication']):
                print('✅ Response includes medication information!')
            else:
                print('❌ Response seems generic, not using patient data')
                
        else:
            print(f'❌ Error: {response.text}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

def test_emergency_contact_question():
    """Test asking about emergency contacts."""
    qa_data = {'question': 'Who should I contact in case of emergency?'}
    
    try:
        response = requests.post('http://localhost:8000/api/v1/ask-question-enhanced/P000001', 
                               json=qa_data, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            print('\n✅ Emergency Contact Response:')
            print(f'Answer: {result["answer"][:200]}...')
        else:
            print(f'\n❌ Emergency Contact Error: {response.text}')
            
    except Exception as e:
        print(f'\n❌ Emergency Contact Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Q&A with Patient-Specific Data")
    print("=" * 60)
    
    test_medication_question()
    test_emergency_contact_question()
    
    print("\n" + "=" * 60)
    print("💡 The Q&A should provide specific information about:")
    print("   - Patient's actual medications (Prednisone, etc.)")
    print("   - Patient's medical conditions")
    print("   - Specific discharge instructions")
    print("   - Not just generic medical advice")
