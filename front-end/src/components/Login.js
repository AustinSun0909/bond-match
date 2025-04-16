// src/components/Login.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import api from '../api';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // 向后端请求获取 JWT Token；确保后端服务器已启动并访问地址正确
      const response = await api.post('/token/', { username, password });
      
      // 将 token 保存到 localStorage（或你喜欢的状态管理中）
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      // 设置默认 axios 请求头，后续请求自动带上 token
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
      // 登录成功后跳转到 Dashboard 或主页面（你后续可创建 Dashboard 页面）
      navigate('/dashboard');
    } catch (err) {
      setError('登录失败，请检查用户名或密码');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          登录
        </Typography>
        <form onSubmit={handleLogin}>
          <TextField
            label="用户名"
            variant="outlined"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            label="密码"
            type="password"
            variant="outlined"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && (
            <Typography color="error" variant="body2">
              {error}
            </Typography>
          )}
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
          >
            登录
          </Button>
        </form>
      </Box>
    </Container>
  );
};

export default Login;
