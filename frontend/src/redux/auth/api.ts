import axios from 'axios';
import { LoginCredentials, RegisterCredentials, AuthResponse, User } from './types';

// Базовый URL для API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Создаем экземпляр axios с базовым URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // Добавляем таймаут для запросов, чтобы они не висели слишком долго
  timeout: 5000
});

// Интерцептор для добавления токена к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

/**
 * API функции для работы с авторизацией
 */
export const authApi = {
  /**
   * Авторизация пользователя
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await api.post<AuthResponse>('/login', credentials);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Ошибка авторизации');
      }
      throw new Error('Ошибка соединения с сервером');
    }
  },

  /**
   * Регистрация нового пользователя
   */
  register: async (userData: RegisterCredentials): Promise<User> => {
    try {
      // Проверка минимальной длины пароля
      if (userData.password.length < 8) {
        throw new Error('Пароль должен содержать минимум 8 символов');
      }
      
      const response = await api.post<User>('/users/', userData);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Ошибка регистрации');
      }
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Ошибка соединения с сервером');
    }
  },

  /**
   * Получение данных текущего пользователя
   */
  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await api.get<User>('/users/me');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Ошибка получения данных пользователя');
      }
      throw new Error('Ошибка соединения с сервером');
    }
  },

  /**
   * Выход пользователя (очистка localStorage)
   */
  logout: (): void => {
    localStorage.removeItem('token');
  },
};

export default api; 