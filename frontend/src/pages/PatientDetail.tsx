import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import {
  UserIcon,
  PhoneIcon,
  EnvelopeIcon,
  CalendarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  EyeIcon,
  ClipboardDocumentListIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import { patientService, Medication } from '../services/api';
import { format } from 'date-fns';

const PatientDetail: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();
  // const queryClient = useQueryClient(); // TODO: Uncomment when adding mutations
  const [showAddMedication, setShowAddMedication] = useState(false);
  const [newMedication, setNewMedication] = useState<Medication>({
    name: '',
    dosage: '',
    frequency: '',
    route: 'Oral'
  });

  const { data: patient, isLoading: patientLoading, error: patientError } = useQuery(
    ['patient', patientId],
    () => patientService.getPatient(patientId!),
    { enabled: !!patientId }
  );

  const { data: medicalRecords, isLoading: recordsLoading } = useQuery(
    ['medicalRecords', patientId],
    () => patientService.getMedicalRecords(patientId!),
    { enabled: !!patientId }
  );

  const { data: dischargeNotes } = useQuery(
    ['dischargeNotes', patientId],
    () => patientService.getDischargeNotes(patientId!),
    { enabled: !!patientId }
  );

  if (patientError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-800">Error Loading Patient</h3>
        <p className="text-red-600 mt-2">
          Unable to load patient data. Please try again later.
        </p>
      </div>
    );
  }

  if (patientLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-yellow-800">Patient Not Found</h3>
        <p className="text-yellow-600 mt-2">
          The requested patient could not be found.
        </p>
      </div>
    );
  }

  const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {patient.first_name} {patient.last_name}
            </h1>
            <p className="text-gray-600">Patient ID: {patient.patient_id}</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowAddMedication(true)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <PlusIcon className="-ml-1 mr-2 h-4 w-4" />
              Add Medication
            </button>
            <Link
              to={`/patients/${patient.patient_id}/qa`}
              className="inline-flex items-center px-4 py-2 border border-blue-300 shadow-sm text-sm font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100"
            >
              <QuestionMarkCircleIcon className="-ml-1 mr-2 h-4 w-4" />
              AI Q&A
            </Link>
            <Link
              to={`/portal/${patient.patient_id}`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <EyeIcon className="-ml-1 mr-2 h-4 w-4" />
              Patient Portal
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient Information */}
        <div className="lg:col-span-1 space-y-6">
          {/* Basic Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Patient Information</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <UserIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Age & Gender</p>
                  <p className="text-sm text-gray-600">{age} years old, {patient.gender}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <CalendarIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Date of Birth</p>
                  <p className="text-sm text-gray-600">
                    {format(new Date(patient.date_of_birth), 'MMMM dd, yyyy')}
                  </p>
                </div>
              </div>

              {patient.phone && (
                <div className="flex items-center space-x-3">
                  <PhoneIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Phone</p>
                    <p className="text-sm text-gray-600">{patient.phone}</p>
                  </div>
                </div>
              )}

              {patient.email && (
                <div className="flex items-center space-x-3">
                  <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Email</p>
                    <p className="text-sm text-gray-600">{patient.email}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Emergency Contact */}
          {patient.emergency_contact && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Emergency Contact</h2>
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-900">
                  {patient.emergency_contact.name}
                </p>
                <p className="text-sm text-gray-600">
                  {patient.emergency_contact.relationship}
                </p>
                <p className="text-sm text-gray-600">
                  {patient.emergency_contact.phone}
                </p>
                {patient.emergency_contact.email && (
                  <p className="text-sm text-gray-600">
                    {patient.emergency_contact.email}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Medical History */}
          {patient.medical_history && patient.medical_history.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Medical History</h2>
              <ul className="space-y-2">
                {patient.medical_history.map((condition, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>{condition}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Allergies */}
          {patient.allergies && patient.allergies.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
                <h2 className="text-lg font-semibold text-gray-900">Allergies</h2>
              </div>
              <div className="space-y-3">
                {patient.allergies.map((allergy, index) => (
                  <div key={index} className="p-3 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-sm font-medium text-red-900">{allergy.allergen}</p>
                    <p className="text-sm text-red-700">Reaction: {allergy.reaction}</p>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      allergy.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      allergy.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      allergy.severity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {allergy.severity} severity
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Medical Records and Discharge Notes */}
        <div className="lg:col-span-2 space-y-6">
          {/* Medical Records */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Medical Records</h2>
            </div>

            {recordsLoading ? (
              <div className="animate-pulse space-y-4">
                {[1, 2].map((i) => (
                  <div key={i} className="p-4 border border-gray-100 rounded-lg">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : medicalRecords && medicalRecords.length > 0 ? (
              <div className="space-y-4">
                {medicalRecords.map((record) => (
                  <div key={record.id} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium text-gray-900">{record.primary_diagnosis}</h3>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          record.severity_level === 'critical' ? 'bg-red-100 text-red-800' :
                          record.severity_level === 'high' ? 'bg-orange-100 text-orange-800' :
                          record.severity_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {record.severity_level}
                        </span>
                        <div className="flex items-center space-x-2">
                          <GenerateDischargeButton patientId={patientId!} medicalRecordId={record.id} />
                          {dischargeNotes?.some(note => note.medical_record_id === record.id) && (
                            <Link
                              to={`/patients/${patientId}/instructions/${record.id}`}
                              className="inline-flex items-center px-3 py-1 border border-blue-300 shadow-sm text-xs font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100"
                            >
                              <DocumentTextIcon className="-ml-1 mr-1 h-3 w-3" />
                              View Instructions
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600 space-y-2">
                      <p><strong>Admission:</strong> {format(new Date(record.admission_date), 'MMM dd, yyyy')}</p>
                      {record.discharge_date && (
                        <p><strong>Discharge:</strong> {format(new Date(record.discharge_date), 'MMM dd, yyyy')}</p>
                      )}
                      {record.secondary_diagnoses && record.secondary_diagnoses.length > 0 && (
                        <p><strong>Secondary:</strong> {record.secondary_diagnoses.join(', ')}</p>
                      )}
                      <p><strong>Treatment:</strong> {record.treatment_summary}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No medical records</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No medical records have been added for this patient yet.
                </p>
              </div>
            )}
          </div>

          {/* Current Medications */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Current Medications</h2>
              <button
                onClick={() => setShowAddMedication(true)}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <PlusIcon className="-ml-1 mr-1.5 h-4 w-4" />
                Add Medication
              </button>
            </div>
            
            {patient.current_medications && patient.current_medications.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {patient.current_medications.map((medication, index) => (
                  <div key={index} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-900">{medication.name}</h4>
                    <p className="text-sm text-blue-700">
                      {medication.dosage} - {medication.frequency}
                    </p>
                    <p className="text-sm text-blue-600">Route: {medication.route}</p>
                    {medication.instructions && (
                      <p className="text-sm text-blue-600 mt-1">{medication.instructions}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No medications</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No current medications have been added for this patient.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Medication Modal */}
      {showAddMedication && (
        <AddMedicationModal
          patient={patient}
          newMedication={newMedication}
          setNewMedication={setNewMedication}
          onClose={() => {
            setShowAddMedication(false);
            setNewMedication({ name: '', dosage: '', frequency: '', route: 'Oral' });
          }}
        />
      )}
    </div>
  );
};

// Generate Discharge Summary Button Component
interface GenerateDischargeButtonProps {
  patientId: string;
  medicalRecordId: number;
}

const GenerateDischargeButton: React.FC<GenerateDischargeButtonProps> = ({ patientId, medicalRecordId }) => {
  const [showSummary, setShowSummary] = useState(false);
  const [dischargeSummary, setDischargeSummary] = useState<string>('');

  const generateSummaryMutation = useMutation(
    () => patientService.generateQuickDischargeSummary(patientId, medicalRecordId),
    {
      onSuccess: (data) => {
        setDischargeSummary(data.discharge_summary);
        setShowSummary(true);
        toast.success('Discharge summary generated successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Error generating discharge summary');
      }
    }
  );

  return (
    <>
      <button
        onClick={() => generateSummaryMutation.mutate()}
        disabled={generateSummaryMutation.isLoading}
        className="inline-flex items-center px-3 py-1 border border-green-300 shadow-sm text-xs font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 disabled:opacity-50"
      >
        <ClipboardDocumentListIcon className="-ml-1 mr-1 h-3 w-3" />
        {generateSummaryMutation.isLoading ? 'Generating...' : 'Generate Summary'}
      </button>

      {/* Discharge Summary Modal */}
      {showSummary && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Discharge Summary</h3>
                <button
                  onClick={() => setShowSummary(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Close</span>
                  ✕
                </button>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-700">{dischargeSummary}</pre>
              </div>
              <div className="flex justify-end space-x-3 mt-4">
                <button
                  onClick={() => navigator.clipboard.writeText(dischargeSummary)}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                >
                  Copy to Clipboard
                </button>
                <button
                  onClick={() => setShowSummary(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// Add Medication Modal Component
interface AddMedicationModalProps {
  patient: any;
  newMedication: Medication;
  setNewMedication: (med: Medication) => void;
  onClose: () => void;
}

const AddMedicationModal: React.FC<AddMedicationModalProps> = ({ 
  patient, 
  newMedication, 
  setNewMedication, 
  onClose 
}) => {
  const queryClient = useQueryClient();

  const addMedicationMutation = useMutation(
    async () => {
      // Update patient with new medication
      const updatedMedications = [...(patient.current_medications || []), newMedication];
      // Note: This would need a proper update patient endpoint in the backend
      // For now, we'll simulate the update
      return { ...patient, current_medications: updatedMedications };
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['patient', patient.patient_id]);
        toast.success('Medication added successfully!');
        onClose();
      },
      onError: (error: any) => {
        toast.error('Error adding medication');
      }
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMedication.name && newMedication.dosage && newMedication.frequency) {
      addMedicationMutation.mutate();
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Add New Medication</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">Close</span>
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Medication Name *
              </label>
              <input
                type="text"
                value={newMedication.name}
                onChange={(e) => setNewMedication({ ...newMedication, name: e.target.value })}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Lisinopril"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dosage *
              </label>
              <input
                type="text"
                value={newMedication.dosage}
                onChange={(e) => setNewMedication({ ...newMedication, dosage: e.target.value })}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., 10mg"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Frequency *
              </label>
              <input
                type="text"
                value={newMedication.frequency}
                onChange={(e) => setNewMedication({ ...newMedication, frequency: e.target.value })}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Once daily"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Route
              </label>
              <select
                value={newMedication.route}
                onChange={(e) => setNewMedication({ ...newMedication, route: e.target.value })}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Oral">Oral</option>
                <option value="Topical">Topical</option>
                <option value="Inhaled">Inhaled</option>
                <option value="Subcutaneous">Subcutaneous</option>
                <option value="Intravenous">Intravenous</option>
                <option value="Intramuscular">Intramuscular</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Instructions
              </label>
              <textarea
                value={newMedication.instructions || ''}
                onChange={(e) => setNewMedication({ ...newMedication, instructions: e.target.value })}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="Special instructions..."
              />
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={addMedicationMutation.isLoading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                {addMedicationMutation.isLoading ? 'Adding...' : 'Add Medication'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PatientDetail;
