import axios from 'axios';

const API_BASE_URL = 'https://web-production-f3389.up.railway.app/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Types
export interface Patient {
  id: number;
  patient_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  phone?: string;
  email?: string;
  emergency_contact?: EmergencyContact;
  medical_history?: string[];
  allergies?: Allergy[];
  current_medications?: Medication[];
  created_at: string;
  updated_at?: string;
}

export interface EmergencyContact {
  name: string;
  relationship: string;
  phone: string;
  email?: string;
}

export interface Allergy {
  allergen: string;
  reaction: string;
  severity: 'low' | 'moderate' | 'high' | 'critical';
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date?: string;
  end_date?: string;
  instructions?: string;
}

export interface MedicalRecord {
  id: number;
  patient_id: string;
  admission_date: string;
  discharge_date?: string;
  primary_diagnosis: string;
  secondary_diagnoses?: string[];
  procedures_performed?: string[];
  treatment_summary: string;
  physician_notes?: string;
  nursing_notes?: string;
  lab_results?: LabResult[];
  vital_signs?: VitalSigns[];
  severity_level: string;
  created_at: string;
  updated_at?: string;
}

export interface LabResult {
  test_name: string;
  value: string;
  unit: string;
  reference_range: string;
  status: string;
  recorded_at: string;
}

export interface VitalSigns {
  temperature?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
  recorded_at: string;
}

export interface DischargeNote {
  id: number;
  patient_id: string;
  medical_record_id: number;
  discharge_summary: string;
  medications_at_discharge?: Medication[];
  follow_up_instructions?: string;
  activity_restrictions?: string;
  diet_instructions?: string;
  warning_signs?: string;
  discharge_physician: string;
  discharge_date: string;
  created_at: string;
}

export interface PersonalizedInstructions {
  medication_schedule: MedicationSchedule[];
  lifestyle_recommendations: string[];
  follow_up_reminders: FollowUpReminder[];
  warning_signs: string[];
  activity_guidelines: string[];
  diet_recommendations: string[];
  wound_care_instructions?: string[];
  emergency_contacts: EmergencyContactInfo[];
  summary: string;
}

export interface MedicationSchedule {
  name: string;
  dosage: string;
  timing: string;
  instructions: string;
  duration?: string;
}

export interface FollowUpReminder {
  type: string;
  timeframe: string;
  purpose: string;
  contact_info?: string;
}

export interface EmergencyContactInfo {
  name: string;
  phone: string;
  type: string;
  when_to_call?: string;
}

export interface QAResponse {
  question: string;
  answer: string;
  confidence: number;
  related_topics: string[];
}

// Patient Service
export const patientService = {
  // Get all patients
  getPatients: async (search?: string): Promise<Patient[]> => {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    const response = await api.get(`/patients/${params}`);
    return response.data;
  },

  // Search patients
  searchPatients: async (query: string): Promise<Patient[]> => {
    const response = await api.get(`/patients/search/${encodeURIComponent(query)}`);
    return response.data;
  },

  // Get patient by ID
  getPatient: async (patientId: string): Promise<Patient> => {
    const response = await api.get(`/patients/${patientId}`);
    return response.data;
  },

  // Create new patient
  createPatient: async (patientData: Omit<Patient, 'id' | 'created_at' | 'updated_at'>): Promise<Patient> => {
    const response = await api.post('/patients/', patientData);
    return response.data;
  },

  // Get medical records for patient
  getMedicalRecords: async (patientId: string): Promise<MedicalRecord[]> => {
    const response = await api.get(`/medical-records/${patientId}`);
    return response.data;
  },

  // Create medical record
  createMedicalRecord: async (recordData: Omit<MedicalRecord, 'id' | 'created_at' | 'updated_at'>): Promise<MedicalRecord> => {
    const response = await api.post('/medical-records/', recordData);
    return response.data;
  },

  // Get discharge notes for patient
  getDischargeNotes: async (patientId: string): Promise<DischargeNote[]> => {
    const response = await api.get(`/discharge-notes/${patientId}`);
    return response.data;
  },

  // Create discharge note
  createDischargeNote: async (noteData: Omit<DischargeNote, 'id' | 'created_at'>): Promise<DischargeNote> => {
    const response = await api.post('/discharge-notes/', noteData);
    return response.data;
  },

  // Generate personalized instructions
  generateInstructions: async (patientId: string, medicalRecordId: number): Promise<PersonalizedInstructions> => {
    const response = await api.post(`/generate-instructions/${patientId}?medical_record_id=${medicalRecordId}`);
    return response.data;
  },

  // Generate quick discharge summary
  generateQuickDischargeSummary: async (patientId: string, medicalRecordId: number): Promise<{
    patient_id: string;
    medical_record_id: number;
    discharge_summary: string;
    generated_at: string;
  }> => {
    const response = await api.post(`/generate-quick-discharge/${patientId}?medical_record_id=${medicalRecordId}`);
    return response.data;
  },

  // Ask question about discharge instructions
  askQuestion: async (patientId: string, question: string, medicalRecordId: number): Promise<QAResponse> => {
    const response = await api.post(`/ask-question/${patientId}?question=${encodeURIComponent(question)}&medical_record_id=${medicalRecordId}`);
    return response.data;
  },

  // Enhanced Q&A with safety measures
  askQuestionEnhanced: async (patientId: string, question: string): Promise<{
    question: string;
    answer: string;
    confidence: number;
    safety_flags: string[];
    sources: string[];
    disclaimer: string;
  }> => {
    const response = await api.post(`/ask-question-enhanced/${patientId}`, {
      question: question
    });
    return response.data;
  },

  // Get comprehensive patient history
  getComprehensiveHistory: async (patientId: string): Promise<{
    patient: any;
    visits: any[];
    activities: any[];
    timeline: any[];
    medical_records: any[];
    discharge_notes: any[];
    total_visits: number;
    total_days_in_hospital: number;
    last_visit_date: string | null;
    current_status: string;
  }> => {
    const response = await api.get(`/patients/${patientId}/comprehensive-history`);
    return response.data;
  },

  // Patient activity logging
  logPatientActivity: async (patientId: string, activityData: {
    activity_type: string;
    description: string;
    details?: any;
    performed_by?: string;
  }) => {
    const response = await api.post(`/patients/${patientId}/activities`, activityData);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; service: string; version: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
