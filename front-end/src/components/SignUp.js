import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup, verifyEmail } from '../services/auth';
import './SignUp.css';

const SignUp = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    verificationCode: ''
  });
  const [step, setStep] = useState(1); // 1: email/password, 2: verification code
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSendCode = async (e) => {
    e.preventDefault();
    setError(null);

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);
    try {
      await signup(formData.email, formData.password);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await verifyEmail(formData.email, formData.verificationCode);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDevSignup = () => {
    // Simulate successful signup by setting a mock token
    localStorage.setItem('auth_token', 'dev_token');
    navigate('/');
  };

  return (
    <div className="signup-container">
      <form onSubmit={step === 1 ? handleSendCode : handleVerifyCode} className="signup-form">
        <h2>Create Account</h2>
        {error && <div className="error-message">{error}</div>}
        
        {step === 1 ? (
          <>
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

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>

            <button type="submit" disabled={loading} className="signup-button">
              {loading ? 'Sending Verification Code...' : 'Send Verification Code'}
            </button>

            <button
              type="button"
              onClick={handleDevSignup}
              className="dev-signup-button"
            >
              Development Signup (Bypass Auth)
            </button>
          </>
        ) : (
          <>
            <div className="verification-message">
              We've sent a verification code to {formData.email}
            </div>
            
            <div className="form-group">
              <label htmlFor="verificationCode">Verification Code</label>
              <input
                type="text"
                id="verificationCode"
                name="verificationCode"
                value={formData.verificationCode}
                onChange={handleChange}
                required
                maxLength="6"
              />
            </div>

            <button type="submit" disabled={loading} className="signup-button">
              {loading ? 'Verifying...' : 'Verify Code'}
            </button>

            <button
              type="button"
              onClick={() => setStep(1)}
              className="back-button"
            >
              Back
            </button>
          </>
        )}

        <p className="login-link">
          Already have an account? <a href="/">Log in</a>
        </p>
      </form>
    </div>
  );
};

export default SignUp; 