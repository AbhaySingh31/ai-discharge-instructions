#!/usr/bin/env python3
"""
Test medication-specific Q&A to verify patient data is being used.
"""

import requests
import json

def test_medication_question():
    """Test asking about medications with patient P000001."""
    qa_data = {'question': 'What medications should I take?'}
    
    try:
        print("🧪 Testing medication question...")
        response = requests.post('http://localhost:8000/api/v1/ask-question-enhanced/P000001', 
                               json=qa_data, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Response received:")
            print(f"Question: {result['question']}")
            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Safety Flags: {result.get('safety_flags', [])}")
            print(f"Sources: {result.get('sources', [])}")
            
            # Check if response mentions specific medications
            answer_lower = result['answer'].lower()
            specific_meds = ['prednisone', 'lisinopril', 'metformin']
            found_meds = [med for med in specific_meds if med in answer_lower]
            
            if found_meds:
                print(f"\n🎉 SUCCESS: Response mentions specific medications: {found_meds}")
                return True
            elif 'taking:' in answer_lower or 'prescribed' in answer_lower:
                print(f"\n✅ GOOD: Response is personalized (mentions prescriptions)")
                return True
            else:
                print(f"\n❌ ISSUE: Response seems generic, not patient-specific")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Testing Patient-Specific Medication Q&A")
    print("=" * 60)
    
    success = test_medication_question()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Q&A is working with patient-specific data!")
        print("✅ The chat interface should now provide personalized responses")
    else:
        print("❌ Q&A still needs improvement for patient-specific responses")
        
    print("\n💡 Try asking in the UI:")
    print("   - 'What medications should I take?'")
    print("   - 'Who is my emergency contact?'")
    print("   - 'What should I watch out for?'")
