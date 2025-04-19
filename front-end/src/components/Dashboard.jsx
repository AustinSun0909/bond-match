import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getCurrentUser } from '../services/auth';
import './Dashboard.css';

const Dashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const handleLogout = () => {
    console.log('Dashboard: Logout button clicked');
    logout();
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>债券匹配系统</h1>
        <div className="user-info">
          <span>欢迎, {currentUser?.username || '用户'}</span>
          <button onClick={handleLogout} className="logout-button">
            登出
          </button>
        </div>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-menu">
          <button onClick={() => navigate('/bonds/search')} className="menu-button">
            债券搜索
          </button>
          <button onClick={() => navigate('/search-history')} className="menu-button">
            搜索历史
          </button>
        </div>
        
        <div className="dashboard-main">
          <h2>债券匹配系统主面板</h2>
          <p>请选择左侧功能进行操作</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 