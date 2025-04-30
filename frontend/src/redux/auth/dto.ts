import { User, AuthResponse } from './types';

/**
 * DTO (Data Transfer Object) функции для преобразования данных
 */
export const authDto = {
  /**
   * Нормализация пользовательских данных 
   * Можно расширить для более сложных преобразований
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
   * Обработка ответа авторизации и сохранение токена
   */
  processAuthResponse: (response: AuthResponse): string => {
    const { access_token, token_type } = response;
    
    // Сохраняем токен и его тип в localStorage, если требуется
    localStorage.setItem('token', access_token);
    localStorage.setItem('token_type', token_type); // сохраняем тип токена
    
    return access_token;
  },

  /**
   * Получение токена из localStorage
   */
  getStoredToken: (): string | null => {
    return localStorage.getItem('token');
  },

  /**
   * Проверка существования токена в localStorage
   */
  hasToken: (): boolean => {
    return !!localStorage.getItem('token');
  },
}; 