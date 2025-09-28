import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  UserGroupIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  UserPlusIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { patientService, Patient } from '../services/api';
import { format } from 'date-fns';

const PatientList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { data: patients, isLoading, error } = useQuery<Patient[]>(
    'patients', 
    () => patientService.getPatients(),
    {
      refetchInterval: 5000, // Refetch every 5 seconds for live updates
      refetchIntervalInBackground: true,
      staleTime: 0 // Always consider data stale for fresh updates
    }
  );

  // Filter patients based on search term
  const filteredPatients = patients?.filter(patient =>
    patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.patient_id.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-800">Error Loading Patients</h3>
        <p className="text-red-600 mt-2">
          Unable to load patient data. Please try again later.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
            <p className="mt-1 text-gray-600">
              Manage patient records and discharge instructions
            </p>
          </div>
          <Link
            to="/patients/new"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            Add Patient
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search patients by name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Patient List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="p-6">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center space-x-4 p-4 border border-gray-100 rounded-lg">
                  <div className="h-12 w-12 bg-gray-200 rounded-full"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/6"></div>
                  </div>
                  <div className="h-8 w-20 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="text-center py-12">
            <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {searchTerm ? 'No patients found' : 'No patients yet'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm 
                ? 'Try adjusting your search terms.' 
                : 'Get started by adding your first patient.'
              }
            </p>
            {!searchTerm && (
              <div className="mt-6">
                <Link
                  to="/patients/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                  Add Patient
                </Link>
              </div>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredPatients.map((patient) => (
              <PatientCard key={patient.id} patient={patient} />
            ))}
          </div>
        )}
      </div>

      {/* Summary */}
      {filteredPatients.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">
            Showing {filteredPatients.length} of {patients?.length || 0} patients
            {searchTerm && ` matching "${searchTerm}"`}
          </p>
        </div>
      )}
    </div>
  );
};

interface PatientCardProps {
  patient: Patient;
}

const PatientCard: React.FC<PatientCardProps> = ({ patient }) => {
  const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear();

  return (
    <div className="p-6 hover:bg-gray-50 transition-colors duration-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
            <UserGroupIcon className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {patient.first_name} {patient.last_name}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>ID: {patient.patient_id}</span>
              <span>Age: {age}</span>
              <span>Gender: {patient.gender}</span>
            </div>
            {patient.phone && (
              <p className="text-sm text-gray-500 mt-1">
                Phone: {patient.phone}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Medical History Badge */}
          {patient.medical_history && patient.medical_history.length > 0 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Medical History
            </span>
          )}

          {/* Allergies Badge */}
          {patient.allergies && patient.allergies.length > 0 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Allergies
            </span>
          )}

          {/* Actions */}
          <div className="flex items-center space-x-2">
            <Link
              to={`/patients/${patient.patient_id}`}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <EyeIcon className="-ml-1 mr-1.5 h-4 w-4" />
              View
            </Link>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          <span>Created: {format(new Date(patient.created_at), 'MMM dd, yyyy')}</span>
          {patient.current_medications && patient.current_medications.length > 0 && (
            <span>{patient.current_medications.length} current medications</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientList;
