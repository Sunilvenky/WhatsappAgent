/**
 * Authentication Service
 * Handles user authentication, registration, and token management
 */
import { post, get } from './api';

/**
 * Login user
 * @param {string} username - Username or email
 * @param {string} password - User password
 * @returns {Promise<Object>} User data and token
 */
export const login = async (username, password) => {
  try {
    // FastAPI OAuth2 expects form data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // Store token and user data
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      
      // Get user profile
      const user = await getCurrentUser();
      localStorage.setItem('user', JSON.stringify(user));
      
      return { ...response, user };
    }
    
    return response;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

/**
 * Register new user
 * @param {Object} userData - User registration data
 * @returns {Promise<Object>} Created user data
 */
export const register = async (userData) => {
  try {
    const response = await post('/auth/register', userData);
    return response;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

/**
 * Get current authenticated user
 * @returns {Promise<Object>} User data
 */
export const getCurrentUser = async () => {
  try {
    const response = await get('/auth/me');
    return response;
  } catch (error) {
    console.error('Get current user error:', error);
    throw error;
  }
};

/**
 * Logout user
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

/**
 * Get stored user data
 * @returns {Object|null}
 */
export const getStoredUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Update user profile
 * @param {Object} userData - User data to update
 * @returns {Promise<Object>} Updated user data
 */
export const updateProfile = async (userData) => {
  try {
    const response = await post('/auth/update-profile', userData);
    
    // Update stored user data
    const user = getStoredUser();
    if (user) {
      const updatedUser = { ...user, ...response };
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
    
    return response;
  } catch (error) {
    console.error('Update profile error:', error);
    throw error;
  }
};

/**
 * Change password
 * @param {string} currentPassword - Current password
 * @param {string} newPassword - New password
 * @returns {Promise<Object>} Response
 */
export const changePassword = async (currentPassword, newPassword) => {
  try {
    const response = await post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response;
  } catch (error) {
    console.error('Change password error:', error);
    throw error;
  }
};

export default {
  login,
  register,
  getCurrentUser,
  logout,
  isAuthenticated,
  getStoredUser,
  updateProfile,
  changePassword,
};
