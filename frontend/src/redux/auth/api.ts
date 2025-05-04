import axios from 'axios';
import { LoginCredentials, RegisterCredentials, AuthResponse, User } from './types';

// Base URL for API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Interceptor for adding token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    const tokenType = localStorage.getItem('token_type') || 'Bearer';
    config.headers['Authorization'] = `${tokenType} ${token}`;
  }
  return config;
});

/**
 * API functions for authentication
 */
export const authApi = {
  /**
   * User authentication
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await api.post<AuthResponse>('/users/login', credentials);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Authentication error');
      }
      throw new Error('Error connecting to server');
    }
  },

  /**
   * Register a new user
   */
  register: async (userData: RegisterCredentials): Promise<User> => {
    try {
      // Check minimum password length
      if (userData.password.length < 8) {
        throw new Error('Password must contain at least 8 characters');
      }
      
      const response = await api.post<User>('/users/', userData);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Registration error');
      }
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error connecting to server');
    }
  },

  /**
   * Get current user data
   */
  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await api.get<User>('/users/me');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Error getting user data');
      }
      throw new Error('Error connecting to server');
    }
  },

  /**
   * User logout (clear localStorage)
   */
  logout: (): void => {
    localStorage.removeItem('token');
    localStorage.removeItem('token_type');
  },
};

export default api; 