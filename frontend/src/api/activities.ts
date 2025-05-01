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
  
  // Debug - логирование запросов
  if (process.env.NODE_ENV !== 'production') {
    console.log('API Request:', {
      url: config.url,
      method: config.method,
      data: config.data,
      params: config.params,
      headers: config.headers
    });
  }
  
  return config;
});

// Интерцептор для логирования ответов
apiClient.interceptors.response.use(
  (response) => {
    // Debug - логирование успешных ответов
    if (process.env.NODE_ENV !== 'production') {
      console.log('API Response Success:', {
        url: response.config.url,
        status: response.status,
        data: response.data,
      });
    }
    return response;
  },
  (error) => {
    // Debug - логирование ошибок
    if (process.env.NODE_ENV !== 'production') {
      console.error('API Response Error:', {
        url: error.config?.url,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
    }
    return Promise.reject(error);
  }
);

// Интерфейс для создания активности
export interface ActivityCreateDto {
  title: string;
  description?: string;
  tags: string[];
}

// Интерфейс для получения активности
export interface ActivityDto {
  id: number;
  title: string;
  description?: string | null;
  start_time: string;
  end_time?: string | null;
  duration?: number | null;
  recorded_time: number;
  timer_status: string;
  last_timer_start?: string | null;
  user_id: number;
  tags: { id: number; name: string }[];
}

// Интерфейс для обновления активности
export interface ActivityUpdateDto {
  title?: string;
  description?: string;
  tags?: string[];
  end_time?: string | null;
  duration?: number;
  recorded_time?: number;
  timer_status?: string;
}

// Интерфейс для управления таймером
export interface TimerActionDto {
  action: 'start' | 'pause' | 'stop' | 'save';
}

// Сервис для работы с активностями
export const activitiesApi = {
  /**
   * Получить список активностей с пагинацией и фильтрацией
   */
  getActivities: async (skip = 0, limit = 15, tag?: string): Promise<ActivityDto[]> => {
    try {
      const params: Record<string, string | number> = { skip, limit };
      if (tag) {
        params.tag = tag;
      }
      
      const response = await apiClient.get('/activities/', { params });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении активностей:', error);
      throw error;
    }
  },

  /**
   * Получить одну активность по ID
   */
  getActivity: async (id: number): Promise<ActivityDto> => {
    try {
      const response = await apiClient.get(`/activities/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при получении активности ${id}:`, error);
      throw error;
    }
  },

  /**
   * Создать новую активность
   */
  createActivity: async (activity: ActivityCreateDto): Promise<ActivityDto> => {
    try {
      const response = await apiClient.post('/activities/', activity);
      return response.data;
    } catch (error) {
      console.error('Ошибка при создании активности:', error);
      throw error;
    }
  },

  /**
   * Обновить существующую активность
   */
  updateActivity: async (id: number, activity: ActivityUpdateDto): Promise<ActivityDto> => {
    try {
      // Проверяем обязательные поля
      if (!activity.title) {
        console.error('Ошибка: поле title обязательно для обновления активности');
        throw new Error('Поле title обязательно для обновления активности');
      }
      
      console.log('Отправка запроса на обновление активности:', {
        id,
        data: activity
      });
      
      const response = await apiClient.put(`/activities/${id}`, activity);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при обновлении активности ${id}:`, error);
      throw error;
    }
  },

  /**
   * Удалить активность
   */
  deleteActivity: async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/activities/${id}`);
    } catch (error) {
      console.error(`Ошибка при удалении активности ${id}:`, error);
      throw error;
    }
  },

  /**
   * Управление таймером активности
   */
  timerAction: async (id: number, action: TimerActionDto): Promise<ActivityDto> => {
    try {
      const response = await apiClient.post(`/activities/${id}/timer`, action);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при выполнении таймер-действия для активности ${id}:`, error);
      throw error;
    }
  },
};

export default activitiesApi; 