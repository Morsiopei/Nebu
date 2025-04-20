import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { fetchUserProfile, logout as apiLogout } from '../services/auth'; // Import API calls
import apiClient from '../services/apiClient'; // For direct use or checking state

// 1. Create Context
const AuthContext = createContext(null);

// 2. Create Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Store user profile data
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Simple flag
  const [isLoading, setIsLoading] = useState(true); // To handle initial auth check

  // Function to check authentication status on initial load or refresh
  const checkAuthStatus = useCallback(async () => {
    setIsLoading(true);
    const token = localStorage.getItem('accessToken'); // Check if token exists
    if (!token) {
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
      return;
    }

    try {
      // Verify token by fetching user profile
      const profile = await fetchUserProfile();
      if (profile) {
        setUser(profile);
        setIsAuthenticated(true);
      } else {
        // Token might be invalid or expired, clear state
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      // Error likely means token is invalid/expired
      console.error("Auth check failed:", error);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check auth status when the provider mounts
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Login function updates state and stores tokens (tokens stored in auth service)
  const login = async (credentials) => {
     setIsLoading(true); // Indicate loading during login process
    try {
      // login service handles token storage
      const userData = await import('../services/auth').then(mod => mod.login(credentials));
      // After successful login and token storage by the service, fetch profile
      await checkAuthStatus(); // Re-check auth status to fetch user profile and set state
      return true; // Indicate success
    } catch (error) {
      console.error("Login failed in context:", error);
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
      throw error; // Re-throw error for the login page to handle
    }
  };


  // Logout function clears state and removes tokens
  const logout = () => {
    apiLogout(); // Call the service function to clear tokens
    setUser(null);
    setIsAuthenticated(false);
    // Optionally redirect here or let ProtectedRoute handle it
    // window.location.href = '/login';
  };

  // Value provided to consuming components
  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuthStatus, // Expose if manual refresh is needed elsewhere
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 3. Create custom hook to use the context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
