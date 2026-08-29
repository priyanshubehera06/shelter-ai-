import axios from 'axios';

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api').trim();
// Ensure no trailing slash on base URL
export const API_BASE_URL = rawBaseUrl.endsWith('/') ? rawBaseUrl.slice(0, -1) : rawBaseUrl;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor to format errors user-friendly
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let friendlyMessage = 'Unable to connect to the ShelterAI simulation server.';
    let errorCode = 'NETWORK_ERROR';
    const status = error.response?.status;

    if (error.response) {
      const data = error.response.data;
      if (data?.error?.message) {
        friendlyMessage = data.error.message;
        errorCode = data.error.code || `HTTP_${status}`;
      } else if (data?.detail) {
        friendlyMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        errorCode = `HTTP_${status}`;
      } else if (status === 400) {
        friendlyMessage = 'Invalid parameter specification sent to simulation engine.';
        errorCode = 'BAD_REQUEST';
      } else if (status === 404) {
        friendlyMessage = 'The requested resource or location could not be found.';
        errorCode = 'NOT_FOUND';
      } else if (status === 422) {
        friendlyMessage = 'Validation failed for the requested physics parameters.';
        errorCode = 'VALIDATION_ERROR';
      } else if (status === 429) {
        friendlyMessage = 'Too many requests. Please slow down and try again.';
        errorCode = 'RATE_LIMITED';
      } else if (status >= 500) {
        friendlyMessage = 'The ShelterAI simulation server encountered an internal error.';
        errorCode = 'SERVER_ERROR';
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      friendlyMessage = 'Simulation request timed out. The computational model is under heavy load.';
      errorCode = 'TIMEOUT';
    }

    const enhancedError = new Error(friendlyMessage);
    (enhancedError as any).code = errorCode;
    (enhancedError as any).status = status;
    (enhancedError as any).originalError = error;

    return Promise.reject(enhancedError);
  }
);
