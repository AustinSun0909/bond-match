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
    
    // Add debugging to see what's being returned
    console.log('API response data:', response.data);
    console.log('Search results:', response.data.results);
    
    // Add search to history in backend
    try {
      await saveSearchToHistory(query, response.data.results.length);
    } catch (historyError) {
      console.error('Failed to save search to history:', historyError);
      // Continue anyway - we have localStorage backup
    }
    
    return response.data.results;
  } catch (error) {
    console.error('Search error details:', error.response || error);
    if (error.response && error.response.data && error.response.data.error) {
      throw new Error(error.response.data.error);
    }
    throw new Error('Failed to search bonds');
  }
};

// Function to save a search to the history in the backend
export const saveSearchToHistory = async (query, resultCount = 0) => {
  try {
    const axiosInstance = await authAxios();
    await axiosInstance.post('/search-history/', {
      query,
      result_count: resultCount
    });
  } catch (error) {
    console.error('Error saving search to history:', error);
    throw error;
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
    
    // Format the data if needed
    if (Array.isArray(response.data)) {
      return response.data.map(item => ({
        query: item.query,
        timestamp: item.timestamp || item.created_at, // Handle different field names
        resultCount: item.result_count || 0
      }));
    }
    
    return response.data;
  } catch (error) {
    console.error('Failed to get search history:', error);
    throw error;
  }
}; 