"""
Enhanced AI service with PII protection and anti-hallucination measures.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class SafeQAResponse(BaseModel):
    """Safe Q&A response with PII protection."""
    question: str
    answer: str
    confidence: float
    safety_flags: List[str]
    sources: List[str]
    disclaimer: str

class EnhancedAIService:
    """Enhanced AI service with safety measures and PII protection."""
    
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
        self.model = "meta-llama/llama-3.2-3b-instruct:free"
        
        # PII patterns to detect and sanitize
        self.pii_patterns = {
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'address_number': r'\b\d{1,5}\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b'
        }
        
        # Medical knowledge base for fact-checking
        self.medical_facts = {
            'medication_interactions': [
                "Always consult healthcare provider before starting new medications",
                "Drug interactions can be serious and life-threatening",
                "Never stop prescribed medications without medical supervision"
            ],
            'emergency_symptoms': [
                "Chest pain, difficulty breathing, severe bleeding require immediate medical attention",
                "Call 911 for life-threatening emergencies",
                "When in doubt, seek immediate medical care"
            ],
            'general_advice': [
                "This information is for educational purposes only",
                "Always follow your healthcare provider's specific instructions",
                "Individual medical conditions require personalized care"
            ]
        }
    
    def sanitize_pii(self, text: str) -> str:
        """Remove or mask PII from text."""
        sanitized = text
        
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type == 'ssn':
                sanitized = re.sub(pattern, 'XXX-XX-XXXX', sanitized)
            elif pii_type == 'phone':
                sanitized = re.sub(pattern, 'XXX-XXX-XXXX', sanitized)
            elif pii_type == 'email':
                sanitized = re.sub(pattern, '[EMAIL_REDACTED]', sanitized)
            elif pii_type == 'credit_card':
                sanitized = re.sub(pattern, 'XXXX-XXXX-XXXX-XXXX', sanitized)
            elif pii_type == 'address_number':
                sanitized = re.sub(pattern, '[ADDRESS_REDACTED]', sanitized)
        
        return sanitized
    
    def prepare_safe_patient_context(self, patient_history: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare patient context with PII protection."""
        safe_context = {}
        
        # Patient basic info (anonymized)
        patient = patient_history.get('patient', {})
        safe_context['patient_info'] = {
            'age_group': self._calculate_age_group(patient.get('date_of_birth')),
            'gender': patient.get('gender'),
            'medical_history': patient.get('medical_history', []),
            'allergies': patient.get('allergies', []),
            'current_medications': patient.get('current_medications', [])
        }
        
        # Medical records (clinical data only)
        medical_records = patient_history.get('medical_records', [])
        safe_context['medical_records'] = []
        for record in medical_records:
            safe_record = {
                'primary_diagnosis': record.get('primary_diagnosis'),
                'secondary_diagnoses': record.get('secondary_diagnoses', []),
                'procedures_performed': record.get('procedures_performed', []),
                'treatment_summary': record.get('treatment_summary'),
                'severity_level': record.get('severity_level'),
                'admission_date': record.get('admission_date'),
                'discharge_date': record.get('discharge_date')
            }
            safe_context['medical_records'].append(safe_record)
        
        # Recent activities (clinical only)
        activities = patient_history.get('activities', [])
        safe_context['recent_activities'] = []
        for activity in activities[:10]:  # Last 10 activities
            if activity.get('activity_type') in ['medication_added', 'medication_removed', 'diagnosis_updated', 'procedure_performed']:
                safe_activity = {
                    'type': activity.get('activity_type'),
                    'description': activity.get('description'),
                    'timestamp': activity.get('timestamp')
                }
                safe_context['recent_activities'].append(safe_activity)
        
        # Visit summary
        visits = patient_history.get('visits', [])
        safe_context['visit_summary'] = {
            'total_visits': len(visits),
            'current_status': patient_history.get('current_status', 'outpatient'),
            'last_visit_type': visits[0].get('visit_type') if visits else None
        }
        
        return safe_context
    
    def _calculate_age_group(self, date_of_birth) -> str:
        """Calculate age group instead of exact age."""
        if not date_of_birth:
            return "unknown"
        
        if isinstance(date_of_birth, str):
            try:
                date_of_birth = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            except:
                return "unknown"
        
        age = (datetime.now() - date_of_birth).days // 365
        
        if age < 18:
            return "pediatric"
        elif age < 35:
            return "young_adult"
        elif age < 55:
            return "middle_aged"
        elif age < 75:
            return "senior"
        else:
            return "elderly"
    
    def validate_medical_response(self, response: str) -> tuple[str, List[str]]:
        """Validate AI response for medical accuracy and safety."""
        safety_flags = []
        
        # Check for dangerous advice
        dangerous_phrases = [
            "stop taking medication",
            "don't need to see doctor",
            "ignore symptoms",
            "self-medicate",
            "home remedy instead"
        ]
        
        response_lower = response.lower()
        for phrase in dangerous_phrases:
            if phrase in response_lower:
                safety_flags.append(f"potentially_dangerous_advice: {phrase}")
        
        # Check for specific medical claims
        specific_claims = [
            "will cure",
            "guaranteed to work",
            "never causes side effects",
            "100% safe",
            "no need for follow-up"
        ]
        
        for claim in specific_claims:
            if claim in response_lower:
                safety_flags.append(f"overconfident_claim: {claim}")
        
        # Add safety disclaimers if needed
        if safety_flags:
            response += "\n\n⚠️ IMPORTANT: This information is for educational purposes only. Always consult your healthcare provider for personalized medical advice."
        
        return response, safety_flags
    
    def answer_patient_question(
        self,
        question: str,
        patient_history: Dict[str, Any],
        context_type: str = "general"
    ) -> SafeQAResponse:
        """Answer patient questions with safety measures."""
        
        if not self.client:
            raise Exception("AI service not available. OpenRouter API key not configured.")
        
        # Sanitize question for PII
        safe_question = self.sanitize_pii(question)
        
        # Prepare safe patient context
        safe_context = self.prepare_safe_patient_context(patient_history)
        
        # Create system prompt with safety guidelines
        system_prompt = """
        You are a healthcare AI assistant providing educational information about patient discharge instructions and medical care. 

        CRITICAL SAFETY GUIDELINES:
        1. NEVER provide specific medical diagnoses or treatment recommendations
        2. ALWAYS emphasize consulting healthcare providers for medical decisions
        3. NEVER suggest stopping or changing medications without medical supervision
        4. NEVER provide emergency medical advice - direct to emergency services
        5. Focus on general education and clarification of existing discharge instructions
        6. If unsure about any medical information, state uncertainty clearly
        7. NEVER make definitive statements about medical outcomes
        8. Protect patient privacy - do not repeat specific personal information

        RESPONSE FORMAT:
        - Provide helpful, educational information
        - Include appropriate medical disclaimers
        - Suggest consulting healthcare providers when appropriate
        - Be empathetic but professionally cautious
        - Focus on supporting existing medical care, not replacing it

        Remember: You are providing educational support, not medical advice.
        """
        
        # Extract specific patient data for personalized responses
        current_medications = safe_context['patient_info']['current_medications']
        medical_history = safe_context['patient_info']['medical_history']
        allergies = safe_context['patient_info']['allergies']
        medical_records = safe_context.get('medical_records', [])
        discharge_notes = safe_context.get('discharge_notes', [])
        
        # Create detailed context for AI
        medications_text = ""
        if current_medications:
            medications_text = "Current Medications:\n"
            for med in current_medications:
                if isinstance(med, dict):
                    med_name = med.get('name', 'Unknown')
                    dosage = med.get('dosage', '')
                    frequency = med.get('frequency', '')
                    medications_text += f"- {med_name} {dosage} {frequency}\n"
        
        diagnoses_text = ""
        if medical_records:
            diagnoses_text = "Recent Diagnoses:\n"
            for record in medical_records:
                if record.get('primary_diagnosis'):
                    diagnoses_text += f"- {record['primary_diagnosis']}\n"
        
        discharge_instructions = ""
        if discharge_notes:
            latest_note = discharge_notes[0]  # Most recent
            if latest_note.get('follow_up_instructions'):
                discharge_instructions += f"Follow-up Instructions: {latest_note['follow_up_instructions']}\n"
            if latest_note.get('activity_restrictions'):
                discharge_instructions += f"Activity Restrictions: {latest_note['activity_restrictions']}\n"
            if latest_note.get('diet_instructions'):
                discharge_instructions += f"Diet Instructions: {latest_note['diet_instructions']}\n"
            if latest_note.get('warning_signs'):
                discharge_instructions += f"Warning Signs: {latest_note['warning_signs']}\n"
        
        user_prompt = f"""
        Based on the following patient's specific medical information, please answer this question: "{safe_question}"

        PATIENT'S SPECIFIC INFORMATION:
        {medications_text}
        
        {diagnoses_text}
        
        Medical History: {', '.join(medical_history) if medical_history else 'None recorded'}
        
        Allergies: {', '.join([allergy.get('allergen', str(allergy)) if isinstance(allergy, dict) else str(allergy) for allergy in allergies]) if allergies else 'No known allergies'}
        
        {discharge_instructions}

        INSTRUCTIONS:
        - Provide specific, personalized information based on this patient's actual medications and conditions
        - Reference their specific medications by name when relevant
        - Address their specific medical conditions and diagnoses
        - Include relevant discharge instructions if applicable
        - Always emphasize following their healthcare provider's specific instructions
        - Be helpful and informative while maintaining medical safety
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent, safer responses
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            # Validate and add safety measures
            safe_response, safety_flags = self.validate_medical_response(ai_response)
            
            # Calculate confidence based on response characteristics
            confidence = self._calculate_confidence(safe_response, safety_flags)
            
            # Add standard medical disclaimer
            disclaimer = (
                "This information is for educational purposes only and should not replace "
                "professional medical advice. Always consult your healthcare provider for "
                "personalized medical guidance and follow their specific instructions."
            )
            
            # Identify sources used
            sources = ["Patient discharge instructions", "General medical education"]
            if safe_context['medical_records']:
                sources.append("Patient medical history")
            
            return SafeQAResponse(
                question=safe_question,
                answer=safe_response,
                confidence=confidence,
                safety_flags=safety_flags,
                sources=sources,
                disclaimer=disclaimer
            )
            
        except Exception as e:
            logger.error(f"Error in AI Q&A: {str(e)}")
            
            # Fallback response for errors
            return SafeQAResponse(
                question=safe_question,
                answer="I apologize, but I'm unable to provide a response at this time. Please consult your healthcare provider for assistance with your question.",
                confidence=0.0,
                safety_flags=["ai_service_error"],
                sources=["Error fallback"],
                disclaimer="AI service temporarily unavailable. Please contact your healthcare provider."
            )
    
    def _calculate_confidence(self, response: str, safety_flags: List[str]) -> float:
        """Calculate confidence score based on response characteristics."""
        base_confidence = 0.8
        
        # Reduce confidence for safety flags
        confidence_penalty = len(safety_flags) * 0.1
        
        # Reduce confidence for uncertain language
        uncertain_phrases = ["might", "could", "possibly", "unsure", "unclear"]
        uncertainty_count = sum(1 for phrase in uncertain_phrases if phrase in response.lower())
        uncertainty_penalty = uncertainty_count * 0.05
        
        # Increase confidence for appropriate disclaimers
        disclaimer_bonus = 0.1 if "consult" in response.lower() and "healthcare" in response.lower() else 0
        
        final_confidence = max(0.1, base_confidence - confidence_penalty - uncertainty_penalty + disclaimer_bonus)
        return min(1.0, final_confidence)
    
    def generate_safe_discharge_summary(self, patient_history: Dict[str, Any]) -> str:
        """Generate discharge summary with PII protection."""
        safe_context = self.prepare_safe_patient_context(patient_history)
        
        # Create a safe summary without PII
        summary_parts = []
        
        # Patient demographics (anonymized)
        patient_info = safe_context['patient_info']
        summary_parts.append(f"Patient: {patient_info['age_group'].title()} {patient_info['gender']}")
        
        # Medical history
        if patient_info['medical_history']:
            summary_parts.append(f"Medical History: {', '.join(patient_info['medical_history'])}")
        
        # Current medications
        if patient_info['current_medications']:
            meds = []
            for med in patient_info['current_medications']:
                if isinstance(med, dict):
                    med_name = med.get('name', 'Unknown medication')
                    dosage = med.get('dosage', '')
                    frequency = med.get('frequency', '')
                    meds.append(f"{med_name} {dosage} {frequency}".strip())
                else:
                    meds.append(str(med))
            summary_parts.append(f"Current Medications: {', '.join(meds)}")
        
        # Allergies
        if patient_info['allergies']:
            allergies = []
            for allergy in patient_info['allergies']:
                if isinstance(allergy, dict):
                    allergen = allergy.get('allergen', 'Unknown allergen')
                    reaction = allergy.get('reaction', '')
                    allergies.append(f"{allergen} ({reaction})".strip())
                else:
                    allergies.append(str(allergy))
            summary_parts.append(f"Allergies: {', '.join(allergies)}")
        
        # Recent medical records
        medical_records = safe_context['medical_records']
        if medical_records:
            latest_record = medical_records[0]
            summary_parts.append(f"Recent Diagnosis: {latest_record.get('primary_diagnosis', 'Not specified')}")
            if latest_record.get('procedures_performed'):
                summary_parts.append(f"Recent Procedures: {', '.join(latest_record['procedures_performed'])}")
        
        return "\n".join(summary_parts)
