// src/api.js
import axios from 'axios';

// 创建一个 Axios 实例，设置基础 URL
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

// 添加响应拦截器
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        // 使用 refresh token 获取新的 access token
        const rs = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
          refresh: refreshToken,
        });
        const { access } = rs.data;
        // 更新 localStorage 和默认请求头
        localStorage.setItem('access_token', access);
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        // 重试原来的请求
        return axios(originalRequest);
      } catch (refreshError) {
        // 刷新失败后，可以选择清除 token 并重定向到登录页
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
