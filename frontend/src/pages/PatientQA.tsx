import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-toastify';
import {
  QuestionMarkCircleIcon,
  PaperAirplaneIcon,
  UserIcon,
  ComputerDesktopIcon,
  ClockIcon,
  HeartIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ShieldCheckIcon,
  CalendarIcon,
  BeakerIcon,
  PlusCircleIcon,
  MinusCircleIcon
} from '@heroicons/react/24/outline';
import { patientService } from '../services/api';
import { format } from 'date-fns';

interface QAMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  confidence?: number;
  safetyFlags?: string[];
  sources?: string[];
  disclaimer?: string;
}

interface ComprehensivePatientHistory {
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
}

const PatientQA: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<QAMessage[]>([]);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overview: true,
    medications: false,
    history: false,
    visits: false,
    timeline: false
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch comprehensive patient history with fallback
  const { data: patientHistory, isLoading: historyLoading, error: historyError } = useQuery<ComprehensivePatientHistory>(
    ['comprehensive-history', patientId],
    async () => {
      try {
        return await patientService.getComprehensiveHistory(patientId!);
      } catch (error) {
        // Fallback: use basic patient data if comprehensive history fails
        const patient = await patientService.getPatient(patientId!);
        return {
          patient: patient,
          visits: [],
          activities: [],
          timeline: [],
          medical_records: [],
          discharge_notes: [],
          total_visits: 0,
          total_days_in_hospital: 0,
          last_visit_date: null,
          current_status: 'outpatient'
        };
      }
    },
    { 
      enabled: !!patientId,
      refetchInterval: 30000, // Refresh every 30 seconds
      retry: 1
    }
  );

  // Fetch patient basic info
  const { data: patient } = useQuery(
    ['patient', patientId],
    () => patientService.getPatient(patientId!),
    { enabled: !!patientId }
  );

  // AI Q&A mutation
  const askQuestionMutation = useMutation(
    ({ question }: { question: string }) =>
      patientService.askQuestionEnhanced(patientId!, question),
    {
      onSuccess: (data) => {
        const aiMessage: QAMessage = {
          id: Date.now().toString() + '_ai',
          type: 'ai',
          content: data.answer,
          timestamp: new Date(),
          confidence: data.confidence,
          safetyFlags: data.safety_flags,
          sources: data.sources,
          disclaimer: data.disclaimer
        };
        setMessages(prev => [...prev, aiMessage]);
        toast.success('Question answered successfully!');
      },
      onError: (error: any) => {
        if (error.response?.status === 503) {
          toast.error('AI service is not available. Please check OpenRouter configuration.');
        } else {
          toast.error(error.response?.data?.detail || 'Error processing question');
        }
      }
    }
  );

  const handleSubmitQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    // Add user message
    const userMessage: QAMessage = {
      id: Date.now().toString() + '_user',
      type: 'user',
      content: question.trim(),
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Send to AI
    askQuestionMutation.mutate({ question: question.trim() });
    setQuestion('');
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (historyLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!patientHistory) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-800">Patient Not Found</h3>
        <p className="text-red-600 mt-2">Unable to load patient information.</p>
      </div>
    );
  }

  const { patient: patientData } = patientHistory;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Patient Q&A - {patientData.first_name} {patientData.last_name}
            </h1>
            <p className="mt-1 text-gray-600">
              Comprehensive patient information and AI-powered assistance
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              patientHistory.current_status === 'inpatient' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {patientHistory.current_status}
            </div>
            <ShieldCheckIcon className="h-6 w-6 text-green-500" title="PII Protected" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient Information Panel */}
        <div className="lg:col-span-1 space-y-4">
          
          {/* Patient Overview */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div 
              className="p-4 cursor-pointer flex items-center justify-between"
              onClick={() => toggleSection('overview')}
            >
              <div className="flex items-center space-x-2">
                <UserIcon className="h-5 w-5 text-blue-500" />
                <h3 className="font-semibold text-gray-900">Patient Overview</h3>
              </div>
              {expandedSections.overview ? <MinusCircleIcon className="h-5 w-5" /> : <PlusCircleIcon className="h-5 w-5" />}
            </div>
            {expandedSections.overview && (
              <div className="px-4 pb-4 space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">Patient ID:</span>
                    <p className="text-gray-900">{patientData.patient_id}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Gender:</span>
                    <p className="text-gray-900">{patientData.gender}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Age:</span>
                    <p className="text-gray-900">
                      {new Date().getFullYear() - new Date(patientData.date_of_birth).getFullYear()} years
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Total Visits:</span>
                    <p className="text-gray-900">{patientHistory.total_visits}</p>
                  </div>
                </div>
                
                {patientData.emergency_contact && (
                  <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                    <h4 className="font-medium text-yellow-800 mb-2">Emergency Contact</h4>
                    <p className="text-sm text-yellow-700">
                      {patientData.emergency_contact.name} ({patientData.emergency_contact.relationship})
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Current Medications */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div 
              className="p-4 cursor-pointer flex items-center justify-between"
              onClick={() => toggleSection('medications')}
            >
              <div className="flex items-center space-x-2">
                <BeakerIcon className="h-5 w-5 text-green-500" />
                <h3 className="font-semibold text-gray-900">Current Medications</h3>
              </div>
              {expandedSections.medications ? <MinusCircleIcon className="h-5 w-5" /> : <PlusCircleIcon className="h-5 w-5" />}
            </div>
            {expandedSections.medications && (
              <div className="px-4 pb-4">
                {patientData.current_medications && patientData.current_medications.length > 0 ? (
                  <div className="space-y-2">
                    {patientData.current_medications.map((med: any, index: number) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900">{med.name}</div>
                        <div className="text-sm text-gray-600">
                          {med.dosage} - {med.frequency}
                        </div>
                        {med.instructions && (
                          <div className="text-xs text-gray-500 mt-1">{med.instructions}</div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No current medications recorded</p>
                )}
              </div>
            )}
          </div>

          {/* Medical History */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div 
              className="p-4 cursor-pointer flex items-center justify-between"
              onClick={() => toggleSection('history')}
            >
              <div className="flex items-center space-x-2">
                <DocumentTextIcon className="h-5 w-5 text-purple-500" />
                <h3 className="font-semibold text-gray-900">Medical History</h3>
              </div>
              {expandedSections.history ? <MinusCircleIcon className="h-5 w-5" /> : <PlusCircleIcon className="h-5 w-5" />}
            </div>
            {expandedSections.history && (
              <div className="px-4 pb-4">
                {patientData.medical_history && patientData.medical_history.length > 0 ? (
                  <ul className="space-y-1">
                    {patientData.medical_history.map((condition: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-center">
                        <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
                        {condition}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm">No medical history recorded</p>
                )}

                {patientData.allergies && patientData.allergies.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium text-red-600 mb-2">Allergies</h4>
                    {patientData.allergies.map((allergy: any, index: number) => (
                      <div key={index} className="p-2 bg-red-50 rounded text-sm text-red-700">
                        <span className="font-medium">{allergy.allergen}</span> - {allergy.reaction}
                        <span className="ml-2 text-xs">({allergy.severity})</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Recent Visits */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div 
              className="p-4 cursor-pointer flex items-center justify-between"
              onClick={() => toggleSection('visits')}
            >
              <div className="flex items-center space-x-2">
                <CalendarIcon className="h-5 w-5 text-indigo-500" />
                <h3 className="font-semibold text-gray-900">Recent Visits</h3>
              </div>
              {expandedSections.visits ? <MinusCircleIcon className="h-5 w-5" /> : <PlusCircleIcon className="h-5 w-5" />}
            </div>
            {expandedSections.visits && (
              <div className="px-4 pb-4">
                {patientHistory.visits && patientHistory.visits.length > 0 ? (
                  <div className="space-y-3">
                    {patientHistory.visits.slice(0, 3).map((visit: any) => (
                      <div key={visit.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900">{visit.visit_number}</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            visit.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {visit.status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          <p>Type: {visit.visit_type}</p>
                          <p>Admitted: {format(new Date(visit.admission_date), 'MMM dd, yyyy')}</p>
                          {visit.discharge_date && (
                            <p>Discharged: {format(new Date(visit.discharge_date), 'MMM dd, yyyy')}</p>
                          )}
                          {visit.department && <p>Department: {visit.department}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No recent visits recorded</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-[600px] flex flex-col">
            
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <QuestionMarkCircleIcon className="h-6 w-6 text-blue-500" />
                <h3 className="font-semibold text-gray-900">AI Medical Assistant</h3>
                <div className="flex items-center space-x-1 ml-auto">
                  <ShieldCheckIcon className="h-4 w-4 text-green-500" />
                  <span className="text-xs text-green-600">PII Protected</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Ask questions about discharge instructions, medications, or general care guidance
              </p>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <ComputerDesktopIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Start a conversation</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Ask me anything about this patient's care, medications, or discharge instructions.
                  </p>
                  <div className="mt-4 space-y-2">
                    <button
                      onClick={() => setQuestion("What medications should this patient take?")}
                      className="block w-full text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded"
                    >
                      "What medications should this patient take?"
                    </button>
                    <button
                      onClick={() => setQuestion("What are the warning signs to watch for?")}
                      className="block w-full text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded"
                    >
                      "What are the warning signs to watch for?"
                    </button>
                    <button
                      onClick={() => setQuestion("When should the patient follow up?")}
                      className="block w-full text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded"
                    >
                      "When should the patient follow up?"
                    </button>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                    message.type === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-900'
                  } rounded-lg px-4 py-2`}>
                    
                    <div className="flex items-center space-x-2 mb-1">
                      {message.type === 'user' ? (
                        <UserIcon className="h-4 w-4" />
                      ) : (
                        <ComputerDesktopIcon className="h-4 w-4" />
                      )}
                      <span className="text-xs opacity-75">
                        {format(message.timestamp, 'HH:mm')}
                      </span>
                      {message.confidence && (
                        <span className="text-xs opacity-75">
                          Confidence: {Math.round(message.confidence * 100)}%
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    
                    {message.safetyFlags && message.safetyFlags.length > 0 && (
                      <div className="mt-2 p-2 bg-yellow-100 rounded text-xs text-yellow-800">
                        <ExclamationTriangleIcon className="h-3 w-3 inline mr-1" />
                        Safety flags detected
                      </div>
                    )}
                    
                    {message.disclaimer && (
                      <div className="mt-2 p-2 bg-blue-100 rounded text-xs text-blue-800">
                        <InformationCircleIcon className="h-3 w-3 inline mr-1" />
                        {message.disclaimer}
                      </div>
                    )}
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-1 text-xs opacity-75">
                        Sources: {message.sources.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {askQuestionMutation.isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                      <span className="text-sm text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200">
              <form onSubmit={handleSubmitQuestion} className="flex space-x-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a question about this patient's care..."
                  className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={askQuestionMutation.isLoading}
                />
                <button
                  type="submit"
                  disabled={!question.trim() || askQuestionMutation.isLoading}
                  className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="h-5 w-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientQA;
