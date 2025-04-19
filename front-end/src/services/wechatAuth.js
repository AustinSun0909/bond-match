const WECHAT_APP_ID = 'YOUR_APP_ID'; // Replace with your WeChat App ID
const WECHAT_REDIRECT_URI = 'http://localhost:3000/auth/wechat/callback'; // Development redirect URI
const WECHAT_STATE = 'bond_match_state'; // For CSRF protection

export const getWeChatAuthUrl = () => {
  try {
    if (!WECHAT_APP_ID || WECHAT_APP_ID === 'YOUR_APP_ID') {
      throw new Error('WeChat App ID is not configured');
    }
    
    const authUrl = `https://open.weixin.qq.com/connect/qrconnect?appid=${WECHAT_APP_ID}&redirect_uri=${encodeURIComponent(WECHAT_REDIRECT_URI)}&response_type=code&scope=snsapi_login&state=${WECHAT_STATE}#wechat_redirect`;
    console.log('Generated WeChat auth URL:', authUrl);
    return authUrl;
  } catch (error) {
    console.error('Error generating WeChat auth URL:', error);
    throw error;
  }
};

export const handleWeChatCallback = async (code) => {
  try {
    console.log('Handling WeChat callback with code:', code);
    
    const response = await fetch('/api/auth/wechat/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'WeChat authentication failed');
    }

    const data = await response.json();
    console.log('WeChat authentication successful:', data);
    
    // Store the token in localStorage
    localStorage.setItem('auth_token', data.token);
    return data;
  } catch (error) {
    console.error('Error handling WeChat callback:', error);
    throw error;
  }
};

export const isAuthenticated = () => {
  const token = localStorage.getItem('auth_token');
  return !!token;
};

export const logout = () => {
  localStorage.removeItem('auth_token');
}; 