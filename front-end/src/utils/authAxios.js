import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create a custom axios instance
const authAxios = axios.create({
  baseURL: API_URL
});

// Add a request interceptor
authAxios.interceptors.request.use(
  async (config) => {
    // Get the token from local storage
    const token = localStorage.getItem('token');
    
    // Log request information
    console.log(`📤 Sending ${config.method?.toUpperCase()} request to ${config.url}`);
    
    // If token exists, add it to the request header
    if (token) {
      console.log(`📝 Adding auth token to request (${token.substring(0, 10)}...)`);
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log('⚠️ No auth token available for request');
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor
authAxios.interceptors.response.use(
  (response) => {
    console.log(`📥 Response received from ${response.config.url}, status: ${response.status}`);
    return response;
  },
  async (error) => {
    console.error(`❌ Response error ${error.response?.status || 'unknown'} from ${error.config?.url || 'unknown URL'}`, error);
    
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('⚙️ Attempting token refresh due to 401 error');
      originalRequest._retry = true;
      
      try {
        // Get refresh token
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!refreshToken) {
          // No refresh token available, logout
          console.error('🚫 No refresh token available');
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          return Promise.reject(error);
        }
        
        // Try to get a new token
        console.log(`🔄 Refreshing token using refresh token (${refreshToken.substring(0, 10)}...)`);
        const response = await axios.post(`${API_URL}/api/token/refresh/`, {
          refresh: refreshToken
        });
        
        // If we got a new token, save it and retry the request
        if (response.data.access) {
          const { access } = response.data;
          console.log(`✅ Token refresh successful, received new token (${access.substring(0, 10)}...)`);
          localStorage.setItem('token', access);
          
          // Update the Authorization header
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          // Retry the request
          console.log('🔁 Retrying original request with new token');
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // Refresh token expired or invalid
        console.error('🚫 Token refresh failed:', refreshError);
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        
        // Optionally redirect to login page
        console.log('🔀 Redirecting to login page after failed token refresh');
        window.location.href = '/login';
        
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default authAxios; 