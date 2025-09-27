import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  UserGroupIcon,
  DocumentTextIcon,
  ChartBarIcon,
  PlusCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { patientService, Patient } from '../services/api';

const Dashboard: React.FC = () => {
  const { data: patients, isLoading } = useQuery<Patient[]>(
    'patients', 
    () => patientService.getPatients(),
    {
      refetchInterval: 5000, // Refetch every 5 seconds for live updates
      refetchIntervalInBackground: true,
      staleTime: 0 // Always consider data stale for fresh updates
    }
  );

  const stats = [
    {
      name: 'Total Patients',
      value: patients?.length || 0,
      icon: UserGroupIcon,
      color: 'bg-blue-500',
      subtitle: 'Live updates every 5s'
    },
    {
      name: 'Active Cases',
      value: 0, // This would need to be calculated from separate medical records API
      icon: ClockIcon,
      color: 'bg-yellow-500',
    },
    {
      name: 'Discharged Today',
      value: 0, // This would need to be calculated based on discharge dates
      icon: DocumentTextIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Pending Instructions',
      value: 0, // This would need to be calculated
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
    },
  ];

  const quickActions = [
    {
      name: 'Add New Patient',
      description: 'Register a new patient in the system',
      href: '/patients/new',
      icon: PlusCircleIcon,
      color: 'bg-blue-600 hover:bg-blue-700',
    },
    {
      name: 'View All Patients',
      description: 'Browse and manage existing patients',
      href: '/patients',
      icon: UserGroupIcon,
      color: 'bg-green-600 hover:bg-green-700',
    },
    {
      name: 'Generate Instructions',
      description: 'Create AI-powered discharge instructions',
      href: '/patients',
      icon: DocumentTextIcon,
      color: 'bg-purple-600 hover:bg-purple-700',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-2 text-gray-600">
              AI-powered personalized patient discharge instructions system
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <ChartBarIcon className="h-12 w-12 text-blue-600" />
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.name}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center">
                <div className={`${stat.color} rounded-lg p-3`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {isLoading ? '...' : stat.value}
                  </p>
                  {stat.subtitle && (
                    <p className="text-xs text-green-600 font-medium">{stat.subtitle}</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.name}
                to={action.href}
                className="group relative bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200"
              >
                <div className="flex items-center space-x-4">
                  <div className={`${action.color} rounded-lg p-3 transition-colors duration-200`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600">
                      {action.name}
                    </h3>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Activity</h2>
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : patients && patients.length > 0 ? (
          <div className="space-y-4">
            {patients.slice(0, 5).map((patient) => (
              <div key={patient.id} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <UserGroupIcon className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {patient.first_name} {patient.last_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      Patient ID: {patient.patient_id}
                    </p>
                  </div>
                </div>
                <Link
                  to={`/patients/${patient.patient_id}`}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No patients yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by adding your first patient.
            </p>
            <div className="mt-6">
              <Link
                to="/patients/new"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusCircleIcon className="-ml-1 mr-2 h-5 w-5" />
                Add Patient
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="h-3 w-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-green-800">API Status</span>
            </div>
            <span className="text-sm text-green-600">Online</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="h-3 w-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-green-800">AI Service</span>
            </div>
            <span className="text-sm text-green-600">Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
