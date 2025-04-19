// src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import SignUp from './components/SignUp';
import BondSearch from './components/BondSearch';
import { isAuthenticated } from './services/auth';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Clear any existing token on app load
    const token = localStorage.getItem('auth_token');
    if (token === 'dev_token') {
      localStorage.removeItem('auth_token');
    }
    
    try {
      setIsLoggedIn(isAuthenticated());
    } catch (err) {
      console.error('Authentication check failed:', err);
      setError('Failed to check authentication status');
    } finally {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="App">
        <header className="App-header">
          <h1>Bond Match</h1>
        </header>
        <main>
          <Routes>
            <Route
              path="/"
              element={
                !isLoggedIn ? (
                  <Login onLogin={() => setIsLoggedIn(true)} />
                ) : (
                  <BondSearch />
                )
              }
            />
            <Route
              path="/signup"
              element={
                !isLoggedIn ? (
                  <SignUp />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
