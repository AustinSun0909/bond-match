import React, { useState } from 'react';
import { getWeChatAuthUrl } from '../services/wechatAuth';
import './WeChatLogin.css';

const WeChatLogin = ({ onLogin }) => {
  const [error, setError] = useState(null);

  const handleWeChatLogin = () => {
    try {
      const authUrl = getWeChatAuthUrl();
      window.location.href = authUrl;
    } catch (err) {
      setError('Failed to initiate WeChat login. Please try again.');
      console.error('WeChat login error:', err);
    }
  };

  return (
    <div className="wechat-login-container">
      {error && <div className="error-message">{error}</div>}
      <button onClick={handleWeChatLogin} className="wechat-login-button">
        <span className="wechat-icon">W</span>
        Login with WeChat
      </button>
    </div>
  );
};

export default WeChatLogin; 