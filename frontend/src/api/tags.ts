import axios from 'axios';
import { API_BASE_URL } from './config';

// API-клиент с авторизацией
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  const tokenType = localStorage.getItem('token_type') || 'Bearer';
  
  if (token) {
    config.headers['Authorization'] = `${tokenType} ${token}`;
  }
  return config;
});

// Интерфейс для тега
export interface TagDto {
  id: number;
  name: string;
}

// Интерфейс для создания тега
export interface TagCreateDto {
  name: string;
}

// Сервис для работы с тегами
export const tagsApi = {
  /**
   * Получить список всех тегов
   */
  getTags: async (skip = 0, limit = 100): Promise<TagDto[]> => {
    try {
      const response = await apiClient.get('/tags/', { params: { skip, limit } });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении списка тегов:', error);
      throw error;
    }
  },

  /**
   * Создать новый тег
   */
  createTag: async (tag: TagCreateDto): Promise<TagDto> => {
    try {
      const response = await apiClient.post('/tags/', tag);
      return response.data;
    } catch (error) {
      console.error('Ошибка при создании тега:', error);
      throw error;
    }
  },
};

export default tagsApi; 