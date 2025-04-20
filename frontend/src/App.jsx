import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext'; // Assuming AuthContext handles auth state

// Import Page Components (Create these files in pages/)
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import FinancePage from './pages/FinancePage';
import HealthPage from './pages/HealthPage';
import EducationPage from './pages/EducationPage';
import AssistantPage from './pages/AssistantPage';
import SettingsPage from './pages/SettingsPage';
import NotFoundPage from './pages/NotFoundPage';

// Import Layout Component (Create this file in components/common/)
import MainLayout from './components/common/Layout'; // Example layout with header/sidebar/etc.

import './styles/global.css'; // Import global styles

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth(); // Get auth status from context

  if (isLoading) {
    // Optional: Show a loading spinner while checking auth status
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }

  // Render the protected component within the layout
  return <MainLayout>{children}</MainLayout>;
}

// Public Route Component (e.g., Login, Register)
function PublicRoute({ children }) {
   const { isAuthenticated, isLoading } = useAuth(); // Get auth status

   if (isLoading) {
      return <div>Loading...</div>;
   }

   if (isAuthenticated) {
      // Redirect to dashboard if already authenticated
      return <Navigate to="/dashboard" replace />;
   }
  // Render public page (no main layout or simple layout)
  return <div>{children}</div>; // Or a specific PublicLayout
}


function App() {
  return (
    <AuthProvider> {/* Wrap entire app in AuthProvider */}
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

          {/* Protected Routes */}
          <Route path="/" element={<ProtectedRoute><Navigate to="/dashboard" replace /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/finance" element={<ProtectedRoute><FinancePage /></ProtectedRoute>} />
          <Route path="/health" element={<ProtectedRoute><HealthPage /></ProtectedRoute>} />
          <Route path="/education" element={<ProtectedRoute><EducationPage /></ProtectedRoute>} />
          <Route path="/assistant" element={<ProtectedRoute><AssistantPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          {/* Add more specific routes, e.g., /finance/accounts/:id */}

          {/* Catch-all Not Found Route */}
          <Route path="*" element={<NotFoundPage />} /> {/* Can be public or inside layout */}
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
