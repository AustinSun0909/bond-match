import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { requestPasswordReset } from '../services/auth';
import './Login.css'; // Reuse login styles

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);

    try {
      await requestPasswordReset(email);
      setMessage('如果该邮箱已注册，我们已发送密码重置链接。请检查您的邮箱。');
    } catch (err) {
      setError('请求处理失败，请稍后重试');
      console.error('Password reset error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>忘记密码</h2>
        
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="email">请输入您的电子邮箱</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <button type="submit" disabled={loading} className="login-button">
          {loading ? '处理中...' : '发送重置链接'}
        </button>
        
        <p className="back-to-login">
          <Link to="/login">返回登录</Link>
        </p>
      </form>
    </div>
  );
};

export default ForgotPassword; 