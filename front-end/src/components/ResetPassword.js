import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { resetPassword } from '../services/auth';
import './ResetPassword.css';

const ResetPassword = () => {
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { uid, token } = useParams();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (formData.newPassword !== formData.confirmPassword) {
      setError('两次输入的密码不一致');
      setLoading(false);
      return;
    }

    try {
      const response = await resetPassword(uid, token, formData.newPassword);
      
      if (response.access) {
        // Store the new tokens
        localStorage.setItem('token', response.access);
        localStorage.setItem('refreshToken', response.refresh);
        
        setSuccess(true);
        
        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          navigate('/');
        }, 2000);
      }
    } catch (err) {
      setError('密码重置链接无效或已过期，请重新申请');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-password-container">
      <form onSubmit={handleSubmit} className="reset-password-form">
        <h2>重设密码</h2>
        {error && <div className="error-message">{error}</div>}
        {success && (
          <div className="success-message">
            密码重置成功，正在跳转...
          </div>
        )}

        <div className="form-group">
          <label htmlFor="newPassword">新密码</label>
          <input
            type="password"
            id="newPassword"
            name="newPassword"
            value={formData.newPassword}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">确认新密码</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>

        <button 
          type="submit" 
          disabled={loading || success} 
          className="submit-button"
        >
          {loading ? '提交中...' : '重设密码'}
        </button>

        {!success && (
          <p className="login-link">
            <Link to="/login">返回登录</Link>
          </p>
        )}
      </form>
    </div>
  );
};

export default ResetPassword; 