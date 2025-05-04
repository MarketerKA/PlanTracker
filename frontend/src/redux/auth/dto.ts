import { User, AuthResponse } from './types';

/**
 * DTO (Data Transfer Object) functions for data transformation
 */
export const authDto = {
  /**
   * Normalize user data
   * Can be extended for more complex transformations
   */
  normalizeUser: (userData: User): User => {
    return {
      id: userData.id,
      email: userData.email,
      is_active: userData.is_active,
      telegram_chat_id: userData.telegram_chat_id,
    };
  },

  /**
   * Process authentication response and save token
   */
  processAuthResponse: (response: AuthResponse): string => {
    const { access_token, token_type } = response;
    
    // Save token and its type in localStorage, if needed
    localStorage.setItem('token', access_token);
    localStorage.setItem('token_type', token_type); // save token type
    
    return access_token;
  },

  /**
   * Get token from localStorage
   */
  getStoredToken: (): string | null => {
    return localStorage.getItem('token');
  },

  /**
   * Check if token exists in localStorage
   */
  hasToken: (): boolean => {
    return !!localStorage.getItem('token');
  },
}; 