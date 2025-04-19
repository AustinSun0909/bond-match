import axios from 'axios';
import { getValidToken } from './auth';

const API_URL = 'http://localhost:8000/api';

// Create an axios instance with authorization header
const authAxios = async () => {
  // Get valid token (will refresh if needed)
  const token = await getValidToken();
  
  // Log token for debugging
  console.log('Using token (truncated):', token ? token.substring(0, 15) + '...' : 'No token');
  
  return axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  });
};

export const searchBonds = async (query) => {
  try {
    const axiosInstance = await authAxios();
    const response = await axiosInstance.get(`/bonds/search/?query=${encodeURIComponent(query)}`);
    return response.data.results;
  } catch (error) {
    console.error('Search error details:', error.response || error);
    if (error.response && error.response.data && error.response.data.error) {
      throw new Error(error.response.data.error);
    }
    throw new Error('Failed to search bonds');
  }
};

export const matchBond = async (bondCode) => {
  try {
    const axiosInstance = await authAxios();
    const response = await axiosInstance.post('/bonds/match/', { bond_code: bondCode });
    return response.data;
  } catch (error) {
    console.error('Bond match error details:', error.response || error);
    if (error.response && error.response.data && error.response.data.error) {
      throw new Error(error.response.data.error);
    }
    throw new Error('Failed to match bond with potential buyers');
  }
};

export const getBondDetails = async (bondCode) => {
  try {
    const axiosInstance = await authAxios();
    const response = await axiosInstance.get(`/bonds/${bondCode}/`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to get bond details');
  }
};

export const getSearchHistory = async () => {
  try {
    const axiosInstance = await authAxios();
    const response = await axiosInstance.get('/search-history/');
    return response.data;
  } catch (error) {
    throw new Error('Failed to get search history');
  }
}; 