import React, { useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { resetPassword } from '../services/auth';
import './Login.css'; // Reuse login styles

const ResetPassword = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useParams();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    
    // Validate passwords match
    if (newPassword !== confirmPassword) {
      setError('密码不匹配');
      return;
    }
    
    setLoading(true);

    try {
      await resetPassword(token, newPassword);
      setMessage('密码重置成功！');
      
      // Redirect to login after a delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('密码重置失败，请稍后重试');
      }
      console.error('Password reset error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>重置密码</h2>
        
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="newPassword">新密码</label>
          <input
            type="password"
            id="newPassword"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">确认密码</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        
        <button type="submit" disabled={loading} className="login-button">
          {loading ? '处理中...' : '重置密码'}
        </button>
        
        <p className="back-to-login">
          <Link to="/login">返回登录</Link>
        </p>
      </form>
    </div>
  );
};

export default ResetPassword; 