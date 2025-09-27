#!/usr/bin/env python3
"""
Test script to verify OpenRouter integration is working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

sys.path.append('backend')

from backend.app.services.ai_agent import DischargeInstructionsAI

def test_openrouter_connection():
    """Test OpenRouter API connection"""
    print("Testing OpenRouter API connection...")
    
    # Initialize AI service
    ai_service = DischargeInstructionsAI()
    
    if not ai_service.client:
        print("❌ OpenRouter client not initialized. Check API key in .env file.")
        return False
    
    print("✅ OpenRouter client initialized successfully")
    print(f"Using model: {ai_service.model}")
    print(f"Base URL: {os.getenv('OPENROUTER_BASE_URL')}")
    
    # Test with sample patient data
    sample_patient = {
        "patient_id": "TEST001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1970-01-01T00:00:00",
        "gender": "male",
        "medical_history": ["Hypertension"],
        "allergies": [],
        "current_medications": []
    }
    
    sample_medical_record = {
        "primary_diagnosis": "Acute myocardial infarction",
        "secondary_diagnoses": [],
        "procedures_performed": ["Cardiac catheterization"],
        "treatment_summary": "Patient underwent successful cardiac catheterization with stent placement.",
        "physician_notes": "Patient stable post-procedure.",
        "severity_level": "high",
        "lab_results": [],
        "vital_signs": []
    }
    
    sample_discharge_note = {
        "discharge_summary": "Patient ready for discharge home with cardiac medications.",
        "medications_at_discharge": [
            {"name": "Aspirin", "dosage": "81mg", "frequency": "daily", "route": "oral"}
        ],
        "follow_up_instructions": "Follow up with cardiologist in 1 week",
        "activity_restrictions": "No heavy lifting for 2 weeks",
        "diet_instructions": "Low sodium diet",
        "warning_signs": "Chest pain, shortness of breath",
        "discharge_physician": "Dr. Smith"
    }
    
    try:
        print("\n🔄 Testing AI instruction generation...")
        instructions = ai_service.generate_personalized_instructions(
            sample_patient,
            sample_medical_record,
            sample_discharge_note
        )
        
        print("✅ AI instruction generation successful!")
        print(f"Generated {len(instructions.medication_schedule)} medication instructions")
        print(f"Generated {len(instructions.warning_signs)} warning signs")
        print(f"Summary: {instructions.summary[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating instructions: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openrouter_connection()
    if success:
        print("\n🎉 OpenRouter integration test passed!")
    else:
        print("\n💥 OpenRouter integration test failed!")
        print("Please check your API key and configuration.")
