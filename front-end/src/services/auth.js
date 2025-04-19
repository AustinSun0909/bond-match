import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const login = async (username, password) => {
  const response = await axios.post(`${API_URL}/api/token/`, {
    username,
    password
  });
  
  // Store tokens in localStorage
  if (response.data.access) {
    localStorage.setItem('token', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);
    
    // Log for debugging
    console.log('Tokens stored:', { 
      access: response.data.access.substring(0, 20) + '...',
      refresh: response.data.refresh.substring(0, 20) + '...'
    });
  }
  
  return response.data;
};

export const signup = async (username, password, email) => {
  // First register the user
  await axios.post(`${API_URL}/api/signup/`, {
    username,
    password,
    email
  });
  
  // Then get tokens through login
  return await login(username, password);
};

export const verifyEmail = async (email, code) => {
  try {
    const response = await fetch('/api/auth/verify-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, code }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Email verification failed');
    }

    const data = await response.json();
    localStorage.setItem('auth_token', data.token);
    return data;
  } catch (error) {
    console.error('Email verification error:', error);
    throw error;
  }
};

export const requestPasswordReset = async (email) => {
  const response = await axios.post(`${API_URL}/api/forgot-password/`, {
    email
  });
  return response.data;
};

export const resetPassword = async (token, newPassword) => {
  const response = await axios.post(`${API_URL}/api/reset-password/`, {
    token,
    newPassword
  });
  return response.data;
};

export const logout = () => {
  console.log('Logging out: Clearing tokens and user data');
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
  // Clear any other potential auth storage
  localStorage.removeItem('auth_token');
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('refreshToken');
  
  // Force a window reload to ensure all state is reset
  window.location.href = '/login';
};

export const getCurrentUser = () => {
  const token = localStorage.getItem('token');
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.user_id,
      username: payload.username
    };
  } catch (error) {
    return null;
  }
};

// Check if token is expired
const isTokenExpired = (token) => {
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiry = payload.exp * 1000; // Convert to milliseconds
    return Date.now() >= expiry;
  } catch (error) {
    console.error('Token validation error:', error);
    return true;
  }
};

// Get valid token or refresh if expired
export const getValidToken = async () => {
  const token = localStorage.getItem('token');
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!token || !refreshToken) {
    return null;
  }
  
  if (!isTokenExpired(token)) {
    // Token is still valid
    return token;
  }
  
  // Token expired, try to refresh
  if (!isTokenExpired(refreshToken)) {
    try {
      const response = await axios.post(`${API_URL}/api/token/refresh/`, {
        refresh: refreshToken
      });
      
      if (response.data.access) {
        localStorage.setItem('token', response.data.access);
        return response.data.access;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      logout(); // Clear tokens if refresh fails
    }
  } else {
    logout(); // Clear tokens if refresh token is also expired
  }
  
  return null;
};

export const isAuthenticated = () => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    console.log('No token found in storage');
    return false;
  }
  
  try {
    // Check if token is a valid JWT format
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.log('Token is not a valid JWT format');
      return false;
    }
    
    // Check expiration
    const payload = JSON.parse(atob(parts[1]));
    const expiry = payload.exp * 1000; // Convert to milliseconds
    const isExpired = Date.now() >= expiry;
    
    if (isExpired) {
      console.log('Token is expired');
      // Don't automatically remove token here as getValidToken will handle refresh
    }
    
    return !isExpired;
  } catch (error) {
    console.error('Token validation error:', error);
    return false;
  }
}; 