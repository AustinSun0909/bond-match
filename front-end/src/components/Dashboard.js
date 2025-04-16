// src/components/Dashboard.js
import React, { useState } from 'react';
import { Container, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import QueryForm from './QueryForm';
import ResultList from './ResultList';

const Dashboard = () => {
  const [results, setResults] = useState([]);
  const [queryError, setQueryError] = useState('');
  const navigate = useNavigate();

  const handleLogout = () => {
    // 清除 token 并跳转到登录页
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete axios.defaults.headers.common['Authorization'];
    navigate('/');
  };

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        仪表盘
      </Typography>
      <Button variant="outlined" color="secondary" onClick={handleLogout}>
        退出登录
      </Button>
      {/* 渲染查询表单 */}
      <QueryForm onResults={setResults} onError={setQueryError} />
      {queryError && (
        <Typography color="error" sx={{ mt: 2 }}>
          {queryError}
        </Typography>
      )}
      {/* 渲染查询结果 */}
      <ResultList results={results} />
    </Container>
  );
};

export default Dashboard;
