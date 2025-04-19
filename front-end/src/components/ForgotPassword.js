import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { requestPasswordReset } from '../services/auth';
import './ForgotPassword.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    try {
      await requestPasswordReset(email);
      setSuccess(true);
      setEmail(''); // Clear the email field after successful submission
    } catch (err) {
      setError('无法发送重置链接，请检查邮箱是否正确');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      <form onSubmit={handleSubmit} className="forgot-password-form">
        <h2>找回密码</h2>
        {error && <div className="error-message">{error}</div>}
        {success && (
          <div className="success-message">
            密码重置链接已发送到您的邮箱，请查收
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="email">注册邮箱</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="请输入您注册时使用的邮箱"
          />
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? '发送中...' : '发送重置链接'}
        </button>

        <p className="login-link">
          <Link to="/login">返回登录</Link>
        </p>
      </form>
    </div>
  );
};

export default ForgotPassword; 