import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-toastify';
import {
  DocumentTextIcon,
  PrinterIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  HeartIcon,
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon
} from '@heroicons/react/24/outline';
import { patientService, QAResponse, MedicationSchedule, FollowUpReminder, EmergencyContactInfo } from '../services/api';
import { format } from 'date-fns';

const DischargeInstructions: React.FC = () => {
  const { patientId, recordId } = useParams<{ patientId: string; recordId: string }>();
  const [question, setQuestion] = useState('');
  const [qaHistory, setQaHistory] = useState<QAResponse[]>([]);

  const { data: patient } = useQuery(
    ['patient', patientId],
    () => patientService.getPatient(patientId!),
    { enabled: !!patientId }
  );

  const { data: instructions, isLoading: instructionsLoading, error: instructionsError } = useQuery(
    ['instructions', patientId, recordId],
    () => patientService.generateInstructions(patientId!, parseInt(recordId!)),
    { 
      enabled: !!patientId && !!recordId,
      retry: 1,
      onError: (error: any) => {
        if (error.response?.status === 503) {
          toast.error('AI service is not available. Please check OpenRouter configuration.');
        } else {
          toast.error('Failed to generate discharge instructions. Please try again.');
        }
      }
    }
  );

  const askQuestionMutation = useMutation(
    ({ question }: { question: string }) =>
      patientService.askQuestion(patientId!, question, parseInt(recordId!)),
    {
      onSuccess: (data) => {
        setQaHistory(prev => [...prev, data]);
        setQuestion('');
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

  const handleAskQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      askQuestionMutation.mutate({ question: question.trim() });
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (instructionsError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-800">Error Loading Instructions</h3>
        <p className="text-red-600 mt-2">
          Unable to generate discharge instructions. Please try again later.
        </p>
      </div>
    );
  }

  if (instructionsLoading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!instructions || !patient) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-yellow-800">Instructions Not Available</h3>
        <p className="text-yellow-600 mt-2">
          Discharge instructions could not be generated for this patient.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 no-print">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Discharge Instructions</h1>
            <p className="text-gray-600">
              Personalized instructions for {patient.first_name} {patient.last_name}
            </p>
          </div>
          <button
            onClick={handlePrint}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <PrinterIcon className="-ml-1 mr-2 h-4 w-4" />
            Print Instructions
          </button>
        </div>
      </div>

      {/* Patient Info Header for Print */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center border-b border-gray-200 pb-4 mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Discharge Instructions</h1>
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p><strong>Patient:</strong> {patient.first_name} {patient.last_name}</p>
              <p><strong>Patient ID:</strong> {patient.patient_id}</p>
            </div>
            <div>
              <p><strong>Date:</strong> {format(new Date(), 'MMMM dd, yyyy')}</p>
              <p><strong>Time:</strong> {format(new Date(), 'h:mm a')}</p>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <DocumentTextIcon className="h-6 w-6 mr-2 text-blue-600" />
            Summary
          </h2>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-gray-800">{instructions.summary}</p>
          </div>
        </div>

        {/* Medication Schedule */}
        {instructions.medication_schedule.length > 0 && (
          <div className="mb-8 print-break">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <ClockIcon className="h-6 w-6 mr-2 text-green-600" />
              Medication Schedule
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {instructions.medication_schedule.map((medication: MedicationSchedule, index: number) => (
                <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900">{medication.name}</h3>
                  <p className="text-green-800"><strong>Dosage:</strong> {medication.dosage}</p>
                  <p className="text-green-800"><strong>Timing:</strong> {medication.timing}</p>
                  <p className="text-green-700 text-sm mt-2">{medication.instructions}</p>
                  {medication.duration && (
                    <p className="text-green-700 text-sm"><strong>Duration:</strong> {medication.duration}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Warning Signs */}
        {instructions.warning_signs.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <ExclamationTriangleIcon className="h-6 w-6 mr-2 text-red-600" />
              Warning Signs - Call Your Doctor Immediately
            </h2>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <ul className="space-y-2">
                {instructions.warning_signs.map((sign: string, index: number) => (
                  <li key={index} className="flex items-start space-x-2 text-red-800">
                    <span className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{sign}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Activity Guidelines */}
        {instructions.activity_guidelines.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <HeartIcon className="h-6 w-6 mr-2 text-purple-600" />
              Activity Guidelines
            </h2>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <ul className="space-y-2">
                {instructions.activity_guidelines.map((guideline: string, index: number) => (
                  <li key={index} className="flex items-start space-x-2 text-purple-800">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{guideline}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Diet Recommendations */}
        {instructions.diet_recommendations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Diet Recommendations</h2>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <ul className="space-y-2">
                {instructions.diet_recommendations.map((recommendation: string, index: number) => (
                  <li key={index} className="flex items-start space-x-2 text-yellow-800">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Lifestyle Recommendations */}
        {instructions.lifestyle_recommendations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Lifestyle Recommendations</h2>
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <ul className="space-y-2">
                {instructions.lifestyle_recommendations.map((recommendation: string, index: number) => (
                  <li key={index} className="flex items-start space-x-2 text-indigo-800">
                    <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Follow-up Reminders */}
        {instructions.follow_up_reminders.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Follow-up Appointments</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {instructions.follow_up_reminders.map((reminder: FollowUpReminder, index: number) => (
                <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900">{reminder.type}</h3>
                  <p className="text-gray-700"><strong>When:</strong> {reminder.timeframe}</p>
                  <p className="text-gray-700"><strong>Purpose:</strong> {reminder.purpose}</p>
                  {reminder.contact_info && (
                    <p className="text-gray-600 text-sm mt-2">{reminder.contact_info}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Wound Care Instructions */}
        {instructions.wound_care_instructions && instructions.wound_care_instructions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Wound Care Instructions</h2>
            <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
              <ol className="space-y-2">
                {instructions.wound_care_instructions.map((instruction: string, index: number) => (
                  <li key={index} className="flex items-start space-x-2 text-pink-800">
                    <span className="bg-pink-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center mt-0.5 flex-shrink-0">
                      {index + 1}
                    </span>
                    <span>{instruction}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}

        {/* Emergency Contacts */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Emergency Contacts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {instructions.emergency_contacts.map((contact: EmergencyContactInfo, index: number) => (
              <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="font-semibold text-red-900">{contact.name}</h3>
                <p className="text-red-800 text-lg font-medium">{contact.phone}</p>
                <p className="text-red-700 text-sm">{contact.type}</p>
                {contact.when_to_call && (
                  <p className="text-red-600 text-sm mt-2">{contact.when_to_call}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Interactive Q&A Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 no-print">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <ChatBubbleLeftRightIcon className="h-6 w-6 mr-2 text-blue-600" />
          Ask Questions About Your Instructions
        </h2>

        {/* Question Form */}
        <form onSubmit={handleAskQuestion} className="mb-6">
          <div className="flex space-x-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your discharge instructions..."
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={askQuestionMutation.isLoading}
            />
            <button
              type="submit"
              disabled={!question.trim() || askQuestionMutation.isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <PaperAirplaneIcon className="-ml-1 mr-2 h-4 w-4" />
              {askQuestionMutation.isLoading ? 'Asking...' : 'Ask'}
            </button>
          </div>
        </form>

        {/* Q&A History */}
        {qaHistory.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Previous Questions & Answers</h3>
            {qaHistory.map((qa, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="mb-3">
                  <p className="font-medium text-gray-900">Q: {qa.question}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-gray-800">A: {qa.answer}</p>
                  <div className="mt-2 flex items-center justify-between text-sm text-gray-600">
                    <span>Confidence: {Math.round(qa.confidence * 100)}%</span>
                    {qa.related_topics.length > 0 && (
                      <span>Related: {qa.related_topics.join(', ')}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {qaHistory.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p>No questions asked yet. Feel free to ask about your discharge instructions!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DischargeInstructions;
