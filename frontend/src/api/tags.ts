import axios from 'axios';
import { API_BASE_URL } from './config';

// API client with authorization
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for adding token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  const tokenType = localStorage.getItem('token_type') ?? 'Bearer';
  
  if (token) {
    config.headers['Authorization'] = `${tokenType} ${token}`;
  }
  return config;
});

// Tag interface
export interface TagDto {
  id: number;
  name: string;
}

// Create tag interface
export interface TagCreateDto {
  name: string;
}

// Service for working with tags
export const tagsApi = {
  /**
   * Get list of all tags
   */
  getTags: async (skip = 0, limit = 100): Promise<TagDto[]> => {
    try {
      const response = await apiClient.get('/tags/', { params: { skip, limit } });
      return response.data;
    } catch (error) {
      console.error('Error getting tags list:', error);
      throw error;
    }
  },

  /**
   * Create new tag
   */
  createTag: async (tag: TagCreateDto): Promise<TagDto> => {
    try {
      const response = await apiClient.post('/tags/', tag);
      return response.data;
    } catch (error) {
      console.error('Error creating tag:', error);
      throw error;
    }
  },
};

export default tagsApi; 