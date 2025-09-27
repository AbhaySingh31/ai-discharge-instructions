import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI
# from langchain.prompts import PromptTemplate
# from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class PersonalizedInstructions(BaseModel):
    medication_schedule: List[Dict[str, Any]]
    lifestyle_recommendations: List[str]
    follow_up_reminders: List[Dict[str, Any]]
    warning_signs: List[str]
    activity_guidelines: List[str]
    diet_recommendations: List[str]
    wound_care_instructions: Optional[List[str]] = None
    emergency_contacts: List[Dict[str, str]]
    summary: str

class QAResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    related_topics: List[str]

class DischargeInstructionsAI:
    def __init__(self, openrouter_api_key: Optional[str] = None, openrouter_base_url: Optional[str] = None):
        api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        base_url = openrouter_base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        if not api_key:
            logger.warning("No OpenRouter API key provided. AI features will not work.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        self.model = "meta-llama/llama-3.2-3b-instruct:free"  # Using free Llama model via OpenRouter
        
    def generate_personalized_instructions(
        self,
        patient_data: Dict[str, Any],
        medical_record: Dict[str, Any],
        discharge_note: Dict[str, Any]
    ) -> PersonalizedInstructions:
        """
        Generate personalized discharge instructions based on patient data,
        medical records, and discharge notes.
        """
        try:
            # Prepare the context for the AI
            context = self._prepare_patient_context(patient_data, medical_record, discharge_note)
            
            # Generate instructions using OpenAI
            instructions_text = self._generate_instructions_with_ai(context)
            
            # Parse and structure the response
            structured_instructions = self._parse_instructions(instructions_text, patient_data)
            
            return structured_instructions
            
        except Exception as e:
            logger.error(f"Error generating personalized instructions: {str(e)}")
            raise

    def _prepare_patient_context(
        self,
        patient_data: Dict[str, Any],
        medical_record: Dict[str, Any],
        discharge_note: Dict[str, Any]
    ) -> str:
        """Prepare comprehensive patient context for AI processing."""
        
        # Calculate patient age
        birth_date = datetime.fromisoformat(patient_data.get("date_of_birth", "").replace("Z", "+00:00"))
        age = (datetime.now() - birth_date).days // 365
        
        context = f"""
        PATIENT INFORMATION:
        - Name: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}
        - Age: {age} years
        - Gender: {patient_data.get('gender', '')}
        - Medical History: {', '.join(patient_data.get('medical_history', []))}
        - Known Allergies: {json.dumps(patient_data.get('allergies', []), indent=2)}
        - Current Medications: {json.dumps(patient_data.get('current_medications', []), indent=2)}
        
        MEDICAL RECORD:
        - Primary Diagnosis: {medical_record.get('primary_diagnosis', '')}
        - Secondary Diagnoses: {', '.join(medical_record.get('secondary_diagnoses', []))}
        - Procedures Performed: {', '.join(medical_record.get('procedures_performed', []))}
        - Treatment Summary: {medical_record.get('treatment_summary', '')}
        - Physician Notes: {medical_record.get('physician_notes', '')}
        - Severity Level: {medical_record.get('severity_level', '')}
        - Lab Results: {json.dumps(medical_record.get('lab_results', []), indent=2)}
        - Vital Signs: {json.dumps(medical_record.get('vital_signs', []), indent=2)}
        
        DISCHARGE INFORMATION:
        - Discharge Summary: {discharge_note.get('discharge_summary', '')}
        - Medications at Discharge: {json.dumps(discharge_note.get('medications_at_discharge', []), indent=2)}
        - Follow-up Instructions: {discharge_note.get('follow_up_instructions', '')}
        - Activity Restrictions: {discharge_note.get('activity_restrictions', '')}
        - Diet Instructions: {discharge_note.get('diet_instructions', '')}
        - Warning Signs: {discharge_note.get('warning_signs', '')}
        - Discharge Physician: {discharge_note.get('discharge_physician', '')}
        """
        
        return context

    def _generate_instructions_with_ai(self, context: str) -> str:
        """Use OpenRouter to generate personalized discharge instructions."""
        
        if not self.client:
            raise Exception("OpenRouter client not initialized. Please check API key configuration.")
        
        system_prompt = """
        You are a specialized healthcare AI assistant that generates personalized, easy-to-understand discharge instructions for patients. Your goal is to create clear, actionable, and patient-friendly instructions that reduce confusion and prevent readmissions.

        GUIDELINES:
        1. Use simple, non-medical language that patients and caregivers can easily understand
        2. Be specific about medication schedules, including exact times and dosages
        3. Provide clear lifestyle recommendations based on the patient's condition
        4. Include specific warning signs that require immediate medical attention
        5. Create a realistic follow-up schedule with reminders
        6. Consider the patient's age, gender, medical history, and current condition
        7. Address potential complications or concerns specific to their diagnosis
        8. Include emergency contact information and when to use it

        FORMAT YOUR RESPONSE AS A STRUCTURED JSON with the following sections:
        - medication_schedule: Array of medication objects with name, dosage, timing, and special instructions
        - lifestyle_recommendations: Array of specific lifestyle changes and recommendations
        - follow_up_reminders: Array of follow-up appointments and reminders with dates and purposes
        - warning_signs: Array of specific symptoms that require immediate medical attention
        - activity_guidelines: Array of activity restrictions and recommendations
        - diet_recommendations: Array of dietary guidelines and restrictions
        - wound_care_instructions: Array of wound care steps (if applicable)
        - emergency_contacts: Array of emergency contact information
        - summary: A brief, encouraging summary of the key points
        """

        user_prompt = f"""
        Based on the following patient information, generate comprehensive, personalized discharge instructions:

        {context}

        Please create detailed, patient-friendly discharge instructions that address all aspects of their care and recovery.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}")
            raise

    def _parse_instructions(self, instructions_text: str, patient_data: Dict[str, Any]) -> PersonalizedInstructions:
        """Parse AI-generated instructions into structured format."""
        
        try:
            # Try to parse as JSON first
            if instructions_text.strip().startswith('{'):
                instructions_dict = json.loads(instructions_text)
            else:
                # If not JSON, use AI to convert to structured format
                instructions_dict = self._convert_to_structured_format(instructions_text)
            
            # Ensure emergency contacts include hospital information
            emergency_contacts = instructions_dict.get('emergency_contacts', [])
            if not any(contact.get('type') == 'hospital' for contact in emergency_contacts):
                emergency_contacts.append({
                    "name": "Hospital Emergency Department",
                    "phone": "911",
                    "type": "emergency",
                    "when_to_call": "Life-threatening emergencies"
                })
            
            return PersonalizedInstructions(
                medication_schedule=instructions_dict.get('medication_schedule', []),
                lifestyle_recommendations=instructions_dict.get('lifestyle_recommendations', []),
                follow_up_reminders=instructions_dict.get('follow_up_reminders', []),
                warning_signs=instructions_dict.get('warning_signs', []),
                activity_guidelines=instructions_dict.get('activity_guidelines', []),
                diet_recommendations=instructions_dict.get('diet_recommendations', []),
                wound_care_instructions=instructions_dict.get('wound_care_instructions'),
                emergency_contacts=emergency_contacts,
                summary=instructions_dict.get('summary', 'Please follow all instructions carefully and contact your healthcare provider with any questions.')
            )
            
        except Exception as e:
            logger.error(f"Error parsing instructions: {str(e)}")
            # Return basic instructions if parsing fails
            return self._generate_fallback_instructions(patient_data)

    def _convert_to_structured_format(self, text: str) -> Dict[str, Any]:
        """Convert unstructured text to structured format using AI."""
        
        prompt = f"""
        Convert the following discharge instructions into a structured JSON format:

        {text}

        Return only valid JSON with these keys:
        - medication_schedule
        - lifestyle_recommendations
        - follow_up_reminders
        - warning_signs
        - activity_guidelines
        - diet_recommendations
        - wound_care_instructions
        - emergency_contacts
        - summary
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error converting to structured format: {str(e)}")
            return {}

    def _generate_fallback_instructions(self, patient_data: Dict[str, Any]) -> PersonalizedInstructions:
        """Generate basic fallback instructions if AI processing fails."""
        
        return PersonalizedInstructions(
            medication_schedule=[{
                "name": "Please consult your discharge paperwork",
                "instructions": "Take medications as prescribed by your doctor"
            }],
            lifestyle_recommendations=[
                "Get adequate rest and sleep",
                "Stay hydrated by drinking plenty of water",
                "Follow up with your healthcare provider as scheduled"
            ],
            follow_up_reminders=[{
                "type": "Primary Care",
                "timeframe": "1-2 weeks",
                "purpose": "Post-discharge check-up"
            }],
            warning_signs=[
                "Severe pain that doesn't improve with medication",
                "High fever (over 101°F)",
                "Difficulty breathing",
                "Signs of infection at surgical site"
            ],
            activity_guidelines=[
                "Gradually increase activity as tolerated",
                "Avoid heavy lifting until cleared by doctor"
            ],
            diet_recommendations=[
                "Eat a balanced, nutritious diet",
                "Stay hydrated"
            ],
            emergency_contacts=[{
                "name": "Emergency Services",
                "phone": "911",
                "type": "emergency"
            }],
            summary="Please follow all discharge instructions and contact your healthcare provider with any questions or concerns."
        )

    def answer_patient_question(
        self,
        question: str,
        patient_context: Dict[str, Any],
        discharge_instructions: PersonalizedInstructions
    ) -> QAResponse:
        """Answer patient questions about their discharge instructions."""
        
        context = f"""
        PATIENT DISCHARGE INSTRUCTIONS:
        {discharge_instructions.model_dump_json(indent=2)}
        
        PATIENT CONTEXT:
        {json.dumps(patient_context, indent=2)}
        """

        system_prompt = """
        You are a helpful healthcare assistant answering patient questions about their discharge instructions. 
        Provide clear, accurate, and reassuring answers based on the patient's specific discharge instructions.
        
        GUIDELINES:
        1. Only answer based on the provided discharge instructions and patient context
        2. Use simple, non-medical language
        3. If the question is about serious symptoms or emergencies, advise contacting healthcare provider
        4. Be empathetic and supportive
        5. If you don't have enough information, recommend contacting their healthcare provider
        6. Provide confidence level (0.0 to 1.0) for your answer
        7. Suggest related topics the patient might want to know about
        """

        user_prompt = f"""
        Patient Question: {question}
        
        Context: {context}
        
        Please provide a helpful answer with confidence level and related topics.
        Format as JSON with keys: answer, confidence, related_topics
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return QAResponse(
                question=question,
                answer=result.get('answer', 'I recommend contacting your healthcare provider for this question.'),
                confidence=result.get('confidence', 0.5),
                related_topics=result.get('related_topics', [])
            )
            
        except Exception as e:
            logger.error(f"Error answering patient question: {str(e)}")
            return QAResponse(
                question=question,
                answer="I'm sorry, I couldn't process your question. Please contact your healthcare provider for assistance.",
                confidence=0.0,
                related_topics=[]
            )
