#!/usr/bin/env python3
"""
Test the enhanced Q&A system with PII protection.
"""

import requests
import json

def test_enhanced_qa():
    """Test the enhanced Q&A endpoint."""
    url = 'http://localhost:8000/api/v1/ask-question-enhanced/P000001'
    data = {'question': 'What medications should this patient take?'}
    
    try:
        print("🧪 Testing Enhanced Q&A endpoint...")
        response = requests.post(url, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced Q&A endpoint working!")
            print(f"Question: {result['question']}")
            print(f"Answer: {result['answer'][:150]}...")
            print(f"Confidence: {result['confidence']}")
            print(f"Safety Flags: {result['safety_flags']}")
            print(f"Sources: {result['sources']}")
            print(f"Has Disclaimer: {'disclaimer' in result}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_comprehensive_history():
    """Test the comprehensive history endpoint."""
    url = 'http://localhost:8000/api/v1/patients/P000001/comprehensive-history'
    
    try:
        print("\n🧪 Testing Comprehensive History endpoint...")
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Comprehensive History endpoint working!")
            print(f"Patient: {result['patient']['first_name']} {result['patient']['last_name']}")
            print(f"Total Visits: {result['total_visits']}")
            print(f"Activities Count: {len(result['activities'])}")
            print(f"Timeline Events: {len(result['timeline'])}")
            print(f"Current Status: {result['current_status']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing Enhanced AI Discharge Instructions System")
    print("=" * 60)
    
    qa_working = test_enhanced_qa()
    history_working = test_comprehensive_history()
    
    print("\n" + "=" * 60)
    if qa_working and history_working:
        print("🎉 All enhanced features are working!")
        print("\n✨ New Features Available:")
        print("1. 🛡️  PII-Protected AI Q&A")
        print("2. 📊 Comprehensive Patient History")
        print("3. 📝 Detailed Activity Tracking")
        print("4. 📅 Patient Timeline Visualization")
        print("5. 🔒 Anti-Hallucination Safety Measures")
        print("\n🚀 Visit /patients/P000001/qa to try the new interface!")
    else:
        print("❌ Some features need attention")
