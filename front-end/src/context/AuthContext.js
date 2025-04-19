import React, { createContext, useState, useEffect, useContext } from 'react';
import { isAuthenticated, logout as authLogout } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check authentication status on mount and when localStorage changes
  useEffect(() => {
    const checkAuth = () => {
      try {
        const authStatus = isAuthenticated();
        console.log('Auth check result:', authStatus);
        setIsLoggedIn(authStatus);
      } catch (err) {
        console.error('Authentication check failed:', err);
        setError('Failed to check authentication status');
        setIsLoggedIn(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();

    // Listen for storage events (for multi-tab logout)
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, []);

  const login = () => {
    setIsLoggedIn(true);
  };

  const logout = () => {
    authLogout();
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isLoggedIn,
        isLoading,
        error,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 