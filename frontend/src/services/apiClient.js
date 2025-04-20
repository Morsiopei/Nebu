import axios from 'axios';

// Get the base URL from environment variables (set by Vite)
// Note: During development with proxy, this base URL might not be directly used by Axios
// for requests starting with '/api', but it's good practice to have it.
// For direct calls or in production build, this is crucial.
const API_BASE_URL = process.env.VITE_API_BASE_URL || '/api'; // Default to relative path for proxy

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Request Interceptor ---
// Add Authorization header with JWT token to outgoing requests
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Replace with your actual token retrieval logic (localStorage, Context, State)
    const token = localStorage.getItem('accessToken'); // Example: Get token from local storage

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    // console.log('Starting Request', config); // Debugging
    return config;
  },
  (error) => {
    // console.error('Request Error Interceptor', error); // Debugging
    return Promise.reject(error);
  }
);

// --- Response Interceptor ---
// Handle common errors or token refresh logic
apiClient.interceptors.response.use(
  (response) => {
    // console.log('Response:', response); // Debugging
    // Any status code within the range of 2xx cause this function to trigger
    return response;
  },
  async (error) => {
    // console.error('Response Error Interceptor', error); // Debugging
    const originalRequest = error.config;

    // Handle specific error codes (e.g., 401 Unauthorized for expired token)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark request to prevent infinite loops
      console.warn('Unauthorized request (401). Attempting token refresh...');

      try {
        // TODO: Implement token refresh logic
        // 1. Get refresh token (from localStorage, secure storage, etc.)
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            console.error('No refresh token found. Redirecting to login.');
             // TODO: Redirect to login page or trigger logout
             window.location.href = '/login'; // Simple redirect example
            return Promise.reject(error);
        }

        // 2. Call your refresh token endpoint (adjust path as needed)
        // Assuming your auth service has a refresh endpoint
        const refreshResponse = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        // 3. Store the new tokens
        const newAccessToken = refreshResponse.data.access;
        // const newRefreshToken = refreshResponse.data.refresh; // Optional: if backend rotates refresh tokens
        localStorage.setItem('accessToken', newAccessToken);
        // if (newRefreshToken) localStorage.setItem('refreshToken', newRefreshToken);
        console.log('Token refreshed successfully.');

        // 4. Update the Authorization header in the original request
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

        // 5. Retry the original request
        return apiClient(originalRequest);

      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // TODO: Handle refresh failure (e.g., clear tokens, logout, redirect to login)
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login'; // Simple redirect example
        return Promise.reject(refreshError); // Reject with the refresh error
      }
    }

    // For other errors, just reject the promise
    return Promise.reject(error);
  }
);

export default apiClient;
