#!/usr/bin/env python3
"""
Test AI endpoints after fixing the OpenRouter configuration.
"""

import requests
import json

def test_ai_instructions():
    """Test the AI instructions endpoint."""
    url = 'http://localhost:8000/api/v1/generate-instructions/P000001'
    params = {'medical_record_id': 1}
    
    try:
        print("🧪 Testing AI Instructions endpoint...")
        response = requests.post(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ AI Instructions endpoint is working!")
            data = response.json()
            print(f"Generated {len(data.get('medication_schedule', []))} medication schedules")
            print(f"Generated {len(data.get('lifestyle_recommendations', []))} lifestyle recommendations")
            print(f"Summary: {data.get('summary', '')[:100]}...")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_ai_qa():
    """Test the AI Q&A endpoint."""
    url = 'http://localhost:8000/api/v1/ask-question/P000001'
    params = {
        'question': 'What medications should I take?',
        'medical_record_id': 1
    }
    
    try:
        print("\n🧪 Testing AI Q&A endpoint...")
        response = requests.post(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ AI Q&A endpoint is working!")
            data = response.json()
            print(f"Question: {data.get('question', '')}")
            print(f"Answer: {data.get('answer', '')[:100]}...")
            print(f"Confidence: {data.get('confidence', 0)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing AI Endpoints with OpenRouter")
    print("=" * 50)
    
    instructions_working = test_ai_instructions()
    qa_working = test_ai_qa()
    
    print("\n" + "=" * 50)
    if instructions_working and qa_working:
        print("🎉 All AI endpoints are working!")
    else:
        print("❌ Some AI endpoints are not working")
