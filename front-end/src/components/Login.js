// src/components/Login.js
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login, requestPasswordReset } from '../services/auth';
import './Login.css';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(formData.email, formData.password);
      onLogin();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await requestPasswordReset(formData.email);
      setError('Password reset instructions have been sent to your email');
      setShowForgotPassword(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDevLogin = () => {
    // Simulate successful login by setting a mock token
    localStorage.setItem('auth_token', 'dev_token');
    onLogin();
  };

  return (
    <div className="login-container">
      <form onSubmit={showForgotPassword ? handleForgotPassword : handleLogin} className="login-form">
        <h2>{showForgotPassword ? 'Reset Password' : 'Login'}</h2>
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        {!showForgotPassword && (
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
        )}

        <button type="submit" disabled={loading} className="login-button">
          {loading
            ? showForgotPassword
              ? 'Sending Reset Instructions...'
              : 'Logging in...'
            : showForgotPassword
              ? 'Send Reset Instructions'
              : 'Login'}
        </button>

        {!showForgotPassword && (
          <button
            type="button"
            onClick={handleDevLogin}
            className="dev-login-button"
          >
            Development Login (Bypass Auth)
          </button>
        )}

        {!showForgotPassword ? (
          <p className="forgot-password">
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="forgot-password-link"
            >
              Forgot Password?
            </button>
          </p>
        ) : (
          <p className="back-to-login">
            <button
              type="button"
              onClick={() => setShowForgotPassword(false)}
              className="back-to-login-link"
            >
              Back to Login
            </button>
          </p>
        )}

        <p className="signup-link">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </form>
    </div>
  );
};

export default Login;
