import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { handleWeChatCallback } from '../services/wechatAuth';
import './WeChatCallback.css';

const WeChatCallback = () => {
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(location.search);
      const code = params.get('code');
      const state = params.get('state');

      if (!code) {
        setError('No authorization code received');
        return;
      }

      try {
        await handleWeChatCallback(code);
        navigate('/'); // Redirect to home page after successful login
      } catch (err) {
        setError(err.message);
      }
    };

    handleCallback();
  }, [location, navigate]);

  if (error) {
    return (
      <div className="callback-container">
        <div className="error-message">
          <h2>Login Failed</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')}>Return to Login</button>
        </div>
      </div>
    );
  }

  return (
    <div className="callback-container">
      <div className="loading-message">
        <h2>Logging in...</h2>
        <p>Please wait while we complete your login.</p>
      </div>
    </div>
  );
};

export default WeChatCallback; 