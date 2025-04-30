// Реэкспорт всех необходимых модулей для публичного API
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

// Экспорт редьюсера как default
export default authReducer;

// Экспорт всех действий для использования в компонентах
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

// Экспорт типов
export type {
  User,
  AuthState,
  LoginCredentials,
  RegisterCredentials,
  AuthResponse,
}; 