import apiClient from './apiClient';

const API_PATH = '/auth'; // Prefix defined in API Gateway for auth service

export const login = async (credentials) => {
  try {
    // Adjust endpoint path based on your auth service's urls.py
    const response = await apiClient.post(`${API_PATH}/token/`, credentials); // Example: Simple JWT obtain pair URL
    // Store tokens upon successful login
    if (response.data.access && response.data.refresh) {
      localStorage.setItem('accessToken', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
    }
    // TODO: Fetch user profile data after login?
    return response.data; // Return user data or just success indication
  } catch (error) {
    console.error('Login failed:', error.response?.data || error.message);
    throw error.response?.data || new Error('Login failed');
  }
};

export const register = async (userData) => {
   try {
    // Adjust endpoint path based on your auth service's urls.py
    const response = await apiClient.post(`${API_PATH}/register/`, userData); // Example registration URL
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error.response?.data || error.message);
    // Pass specific error messages from backend if available
    throw error.response?.data || new Error('Registration failed');
  }
};

export const logout = () => {
  // Simple logout: just remove tokens from local storage
  // TODO: Add backend call to blacklist refresh token if applicable
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  // No need to return anything, or maybe return true for success
};

export const fetchUserProfile = async () => {
    try {
        // Adjust endpoint path
        const response = await apiClient.get(`${API_PATH}/user/me/`); // Example user detail URL
        return response.data;
    } catch (error) {
        console.error('Failed to fetch user profile:', error.response?.data || error.message);
        // Don't necessarily throw here, might just mean user is not logged in
        // Let the calling component handle the error (e.g., redirect to login)
        return null; // Indicate failure or not logged in
    }
};

// Add other auth-related API calls (password reset, etc.) if needed
