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
  const tokenType = localStorage.getItem('token_type') || 'Bearer';
  
  if (token) {
    config.headers['Authorization'] = `${tokenType} ${token}`;
  }
  
  // Debug - request logging
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

// Interceptor for response logging
apiClient.interceptors.response.use(
  (response) => {
    // Debug - successful response logging
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
    // Debug - error logging
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

// Interface for creating activity
export interface ActivityCreateDto {
  title: string;
  description?: string;
  due_date?: string;
  tags: string[];
  scheduled_time?: string;
}

// Interface for retrieving activity
export interface ActivityDto {
  id: number;
  title: string;
  description?: string | null;
  start_time: string;
  end_time?: string | null;
  due_date?: string | null;
  duration?: number | null;
  recorded_time: number;
  timer_status: string;
  last_timer_start?: string | null;
  user_id: number;
  tags: { id: number; name: string }[];
}

// Interface for updating activity
export interface ActivityUpdateDto {
  title?: string;
  description?: string;
  tags?: string[];
  due_date?: string;
  end_time?: string | null;
  duration?: number;
  recorded_time?: number;
  timer_status?: string;
  scheduled_time?: string;
}

// Interface for timer management
export interface TimerActionDto {
  action: 'start' | 'pause' | 'stop' | 'save';
}

// Service for working with activities
export const activitiesApi = {
  /**
   * Get list of activities with pagination and filtering
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
      console.error('Error getting activities:', error);
      throw error;
    }
  },

  /**
   * Get one activity by ID
   */
  getActivity: async (id: number): Promise<ActivityDto> => {
    try {
      const response = await apiClient.get(`/activities/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting activity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create new activity
   */
  createActivity: async (activity: ActivityCreateDto): Promise<ActivityDto> => {
    try {
      const response = await apiClient.post('/activities/', activity);
      return response.data;
    } catch (error) {
      console.error('Error creating activity:', error);
      throw error;
    }
  },

  /**
   * Update existing activity
   */
  updateActivity: async (id: number, activity: ActivityUpdateDto): Promise<ActivityDto> => {
    try {
      // Check required fields
      if (!activity.title) {
        console.error('Error: title field is required for activity update');
        throw new Error('Title field is required for activity update');
      }
      
      console.log('Sending activity update request:', {
        id,
        data: activity
      });
      
      const response = await apiClient.put(`/activities/${id}`, activity);
      return response.data;
    } catch (error) {
      console.error(`Error updating activity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete activity
   */
  deleteActivity: async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/activities/${id}`);
    } catch (error) {
      console.error(`Error deleting activity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Activity timer management
   */
  timerAction: async (id: number, action: TimerActionDto): Promise<ActivityDto> => {
    try {
      const response = await apiClient.post(`/activities/${id}/timer`, action);
      return response.data;
    } catch (error) {
      console.error(`Error executing timer action for activity ${id}:`, error);
      throw error;
    }
  },
};

export default activitiesApi; 