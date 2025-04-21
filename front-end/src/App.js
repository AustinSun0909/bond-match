// src/App.js
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import SignUp from './components/SignUp';
import ForgotPassword from './components/ForgotPassword';
import BondSearch from './components/BondSearch';
import ResetPassword from './components/ResetPassword';
import Dashboard from './components/Dashboard';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

// Protected route wrapper component
const ProtectedRoute = ({ children }) => {
  const { isLoggedIn, isLoading } = useAuth();
  
  // Show loading state while auth is being checked
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>验证中...</p>
      </div>
    );
  }
  
  if (!isLoggedIn) {
    console.log('ProtectedRoute: Not logged in, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Main App Routes component using auth context
const AppRoutes = () => {
  const { isLoggedIn, isLoading, error } = useAuth();

  useEffect(() => {
    console.log('AppRoutes: Auth state updated - isLoggedIn:', isLoggedIn, 'isLoading:', isLoading);
  }, [isLoggedIn, isLoading]);

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>错误</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>重试</button>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          !isLoggedIn ? (
            <Login />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />
      <Route
        path="/signup"
        element={
          !isLoggedIn ? (
            <SignUp />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />
      <Route
        path="/forgot-password"
        element={
          !isLoggedIn ? (
            <ForgotPassword />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />
      <Route
        path="/reset-password/:token"
        element={
          !isLoggedIn ? (
            <ResetPassword />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />
      
      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      
      {/* Redirect routes */}
      <Route path="/" element={<Navigate to={isLoggedIn ? "/dashboard" : "/login"} replace />} />
      <Route path="*" element={<Navigate to={isLoggedIn ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
};

// Main App component with Auth Provider
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <AppRoutes />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
