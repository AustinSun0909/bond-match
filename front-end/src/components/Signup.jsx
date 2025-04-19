import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup } from '../services/authService';
import './Signup.css';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!username || !password) {
            setError('用户名和密码不能为空');
            return;
        }

        try {
            const response = await signup(username, password, email);
            if (response.access) {
                localStorage.setItem('token', response.access);
                localStorage.setItem('refreshToken', response.refresh);
                navigate('/dashboard');
            }
        } catch (err) {
            setError(err.response?.data?.error || '注册失败');
        }
    };

    return (
        <div className="signup-container">
            <div className="signup-box">
                <h2>注册</h2>
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
                    <div className="form-group">
                        <label htmlFor="email">邮箱（用于找回密码）</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="signup-button">注册</button>
                </form>
            </div>
        </div>
    );
};

export default Signup; 