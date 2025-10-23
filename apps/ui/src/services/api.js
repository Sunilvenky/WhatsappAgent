/**
 * Base API configuration and utilities
 */
import axios from 'axios';

// API base URL - uses environment variable or defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message);
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }
    
    // Return error with message
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

/**
 * Generic API request helper
 */
export const apiRequest = async (method, url, data = null, config = {}) => {
  try {
    const response = await api({
      method,
      url,
      data,
      ...config,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * GET request
 */
export const get = (url, config = {}) => apiRequest('GET', url, null, config);

/**
 * POST request
 */
export const post = (url, data, config = {}) => apiRequest('POST', url, data, config);

/**
 * PUT request
 */
export const put = (url, data, config = {}) => apiRequest('PUT', url, data, config);

/**
 * PATCH request
 */
export const patch = (url, data, config = {}) => apiRequest('PATCH', url, data, config);

/**
 * DELETE request
 */
export const del = (url, config = {}) => apiRequest('DELETE', url, null, config);

export default api;
