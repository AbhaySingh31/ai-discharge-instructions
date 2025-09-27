import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-toastify';
import {
  UserIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  PrinterIcon,
  HeartIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { patientService, QAResponse } from '../services/api';
import { format } from 'date-fns';

const PatientPortal: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  const [question, setQuestion] = useState('');
  const [qaHistory, setQaHistory] = useState<QAResponse[]>([]);
  const [selectedRecordId, setSelectedRecordId] = useState<number | null>(null);

  const { data: patient } = useQuery(
    ['patient', patientId],
    () => patientService.getPatient(patientId!),
    { enabled: !!patientId }
  );

  const { data: medicalRecords } = useQuery(
    ['medicalRecords', patientId],
    () => patientService.getMedicalRecords(patientId!),
    { enabled: !!patientId }
  );

  const { data: dischargeNotes } = useQuery(
    ['dischargeNotes', patientId],
    () => patientService.getDischargeNotes(patientId!),
    { enabled: !!patientId }
  );

  // Get the most recent medical record with discharge instructions
  const latestRecordWithInstructions = medicalRecords?.find(record => 
    dischargeNotes?.some(note => note.medical_record_id === record.id)
  );

  const { data: instructions } = useQuery(
    ['instructions', patientId, latestRecordWithInstructions?.id],
    () => patientService.generateInstructions(patientId!, latestRecordWithInstructions!.id),
    { enabled: !!patientId && !!latestRecordWithInstructions }
  );

  const askQuestionMutation = useMutation(
    ({ question }: { question: string }) =>
      patientService.askQuestion(patientId!, question, selectedRecordId || latestRecordWithInstructions!.id),
    {
      onSuccess: (data) => {
        setQaHistory(prev => [...prev, data]);
        setQuestion('');
        toast.success('Question answered successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Error processing question');
      }
    }
  );

  const handleAskQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && (selectedRecordId || latestRecordWithInstructions)) {
      askQuestionMutation.mutate({ question: question.trim() });
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (!patient) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-yellow-800">Patient Not Found</h3>
        <p className="text-yellow-600 mt-2">
          The requested patient portal could not be found.
        </p>
      </div>
    );
  }

  const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg text-white p-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Welcome, {patient.first_name}!</h1>
            <p className="text-blue-100 mt-2">
              Your personalized discharge instructions and health information
            </p>
          </div>
          <div className="text-right">
            <p className="text-blue-100">Patient ID: {patient.patient_id}</p>
            <p className="text-blue-100">Age: {age} years</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient Information Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Patient Summary */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <UserIcon className="h-8 w-8 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">Your Information</h2>
            </div>
            <div className="space-y-3 text-sm">
              <div>
                <p className="font-medium text-gray-900">Full Name</p>
                <p className="text-gray-600">{patient.first_name} {patient.last_name}</p>
              </div>
              <div>
                <p className="font-medium text-gray-900">Date of Birth</p>
                <p className="text-gray-600">{format(new Date(patient.date_of_birth), 'MMMM dd, yyyy')}</p>
              </div>
              {patient.phone && (
                <div>
                  <p className="font-medium text-gray-900">Phone</p>
                  <p className="text-gray-600">{patient.phone}</p>
                </div>
              )}
              {patient.email && (
                <div>
                  <p className="font-medium text-gray-900">Email</p>
                  <p className="text-gray-600">{patient.email}</p>
                </div>
              )}
            </div>
          </div>

          {/* Emergency Contact */}
          {patient.emergency_contact && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Emergency Contact</h2>
              <div className="space-y-2 text-sm">
                <p className="font-medium text-gray-900">{patient.emergency_contact.name}</p>
                <p className="text-gray-600">{patient.emergency_contact.relationship}</p>
                <p className="text-blue-600 font-medium">{patient.emergency_contact.phone}</p>
              </div>
            </div>
          )}

          {/* Allergies Alert */}
          {patient.allergies && patient.allergies.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-3">
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
                <h2 className="text-lg font-semibold text-red-900">Important: Allergies</h2>
              </div>
              <div className="space-y-2">
                {patient.allergies.map((allergy, index) => (
                  <div key={index} className="text-sm">
                    <p className="font-medium text-red-900">{allergy.allergen}</p>
                    <p className="text-red-700">{allergy.reaction}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Discharge Instructions */}
          {instructions ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <DocumentTextIcon className="h-8 w-8 text-green-600" />
                  <h2 className="text-xl font-semibold text-gray-900">Your Discharge Instructions</h2>
                </div>
                <button
                  onClick={handlePrint}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 no-print"
                >
                  <PrinterIcon className="-ml-1 mr-2 h-4 w-4" />
                  Print
                </button>
              </div>

              {/* Summary */}
              <div className="mb-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Summary</h3>
                  <p className="text-blue-800">{instructions.summary}</p>
                </div>
              </div>

              {/* Key Sections */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Medications */}
                {instructions.medication_schedule.length > 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <ClockIcon className="h-5 w-5 text-green-600" />
                      <h3 className="font-semibold text-green-900">Your Medications</h3>
                    </div>
                    <div className="space-y-3">
                      {instructions.medication_schedule.slice(0, 3).map((med, index) => (
                        <div key={index} className="text-sm">
                          <p className="font-medium text-green-900">{med.name}</p>
                          <p className="text-green-700">{med.dosage} - {med.timing}</p>
                        </div>
                      ))}
                      {instructions.medication_schedule.length > 3 && (
                        <p className="text-green-600 text-sm">
                          +{instructions.medication_schedule.length - 3} more medications
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Warning Signs */}
                {instructions.warning_signs.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
                      <h3 className="font-semibold text-red-900">When to Call Your Doctor</h3>
                    </div>
                    <div className="space-y-2">
                      {instructions.warning_signs.slice(0, 3).map((sign, index) => (
                        <p key={index} className="text-sm text-red-800">• {sign}</p>
                      ))}
                      {instructions.warning_signs.length > 3 && (
                        <p className="text-red-600 text-sm">
                          +{instructions.warning_signs.length - 3} more warning signs
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Activity Guidelines */}
                {instructions.activity_guidelines.length > 0 && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <HeartIcon className="h-5 w-5 text-purple-600" />
                      <h3 className="font-semibold text-purple-900">Activity Guidelines</h3>
                    </div>
                    <div className="space-y-2">
                      {instructions.activity_guidelines.slice(0, 3).map((guideline, index) => (
                        <p key={index} className="text-sm text-purple-800">• {guideline}</p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Follow-up */}
                {instructions.follow_up_reminders.length > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h3 className="font-semibold text-yellow-900 mb-3">Follow-up Appointments</h3>
                    <div className="space-y-2">
                      {instructions.follow_up_reminders.map((reminder, index) => (
                        <div key={index} className="text-sm">
                          <p className="font-medium text-yellow-900">{reminder.type}</p>
                          <p className="text-yellow-700">{reminder.timeframe}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Emergency Contacts */}
              <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Emergency Contacts</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {instructions.emergency_contacts.map((contact, index) => (
                    <div key={index} className="text-sm">
                      <p className="font-medium text-gray-900">{contact.name}</p>
                      <p className="text-blue-600 font-medium text-lg">{contact.phone}</p>
                      <p className="text-gray-600">{contact.type}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center py-8">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No Discharge Instructions Available</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Your discharge instructions will appear here once they are generated by your healthcare provider.
                </p>
              </div>
            </div>
          )}

          {/* Q&A Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 no-print">
            <div className="flex items-center space-x-3 mb-6">
              <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Ask Questions</h2>
            </div>

            {instructions && (
              <form onSubmit={handleAskQuestion} className="mb-6">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a question about your discharge instructions..."
                    className="flex-1 border border-gray-300 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={askQuestionMutation.isLoading}
                  />
                  <button
                    type="submit"
                    disabled={!question.trim() || askQuestionMutation.isLoading}
                    className="inline-flex items-center px-6 py-3 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <PaperAirplaneIcon className="-ml-1 mr-2 h-4 w-4" />
                    {askQuestionMutation.isLoading ? 'Asking...' : 'Ask'}
                  </button>
                </div>
              </form>
            )}

            {/* Q&A History */}
            {qaHistory.length > 0 ? (
              <div className="space-y-4">
                {qaHistory.map((qa, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="mb-3">
                      <p className="font-medium text-gray-900">Q: {qa.question}</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-gray-800">{qa.answer}</p>
                      <div className="mt-2 text-sm text-gray-600">
                        <span>Confidence: {Math.round(qa.confidence * 100)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p>No questions asked yet.</p>
                {instructions ? (
                  <p>Feel free to ask about your discharge instructions!</p>
                ) : (
                  <p>Questions will be available once your discharge instructions are ready.</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientPortal;
