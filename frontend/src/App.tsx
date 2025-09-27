import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import PatientList from './pages/PatientList';
import PatientDetail from './pages/PatientDetail';
import CreatePatient from './pages/CreatePatient';
import DischargeInstructions from './pages/DischargeInstructions';
import PatientPortal from './pages/PatientPortal';
import PatientQA from './pages/PatientQA';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/patients" element={<PatientList />} />
              <Route path="/patients/new" element={<CreatePatient />} />
              <Route path="/patients/:patientId" element={<PatientDetail />} />
              <Route path="/patients/:patientId/qa" element={<PatientQA />} />
              <Route path="/patients/:patientId/instructions/:recordId" element={<DischargeInstructions />} />
              <Route path="/portal/:patientId" element={<PatientPortal />} />
            </Routes>
          </main>
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
