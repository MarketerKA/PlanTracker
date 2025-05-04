// Re-exporting all necessary modules for public API
import authReducer, { 
  login, 
  register, 
  logout, 
  getCurrentUser, 
  clearError, 
  resetAuth 
} from './slice';
import { authApi } from './api';
import { authDto } from './dto';
import type { User, AuthState, LoginCredentials, RegisterCredentials, AuthResponse } from './types';

// Export reducer as default
export default authReducer;

// Export all actions for use in components
export {
  // Actions
  login,
  register,
  logout,
  getCurrentUser,
  clearError,
  resetAuth,
  
  // API
  authApi,
  
  // DTO
  authDto,
};

// Export types
export type {
  User,
  AuthState,
  LoginCredentials,
  RegisterCredentials,
  AuthResponse,
}; 