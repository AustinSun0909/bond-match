import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../services/auth';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
    // Initialize with empty string, will be filled by useEffect
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login: contextLogin } = useAuth();  // Get login function from context

    // Load the last used username from localStorage
    useEffect(() => {
        console.log('Checking for lastUsername in localStorage');
        const lastUsername = localStorage.getItem('lastUsername');
        console.log('Last username from localStorage:', lastUsername);
        if (lastUsername) {
            setUsername(lastUsername);
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            console.log('Attempting login with:', { username });
            const response = await login(username, password);
            
            if (response.access) {
                console.log('Login successful, tokens received');
                // Save username to localStorage
                localStorage.setItem('lastUsername', username);
                console.log('Saved username to localStorage:', username);
                
                // Context login updates the app state
                contextLogin();
                navigate('/dashboard');
            }
        } catch (err) {
            console.error('Login error:', err);
            setError('用户名或密码错误');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-form">
                <h2>登录</h2>
                {error && <div className="error-message">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">用户名</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">密码</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button 
                        type="submit" 
                        className="login-button"
                        disabled={isLoading}
                    >
                        {isLoading ? '登录中...' : '登录'}
                    </button>
                </form>
                <div className="forgot-password">
                    <Link to="/forgot-password">忘记密码?</Link>
                </div>
                <div className="signup-link">
                    没有账号? <Link to="/signup">注册</Link>
                </div>
            </div>
        </div>
    );
};

export default Login; 