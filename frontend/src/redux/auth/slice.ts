import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authApi } from './api';
import { authDto } from './dto';
import { 
  AuthState, 
  LoginCredentials, 
  RegisterCredentials, 
  User, 
  AuthResponse 
} from './types';

// Начальное состояние
const initialState: AuthState = {
  user: null,
  token: authDto.getStoredToken(),
  isAuthenticated: authDto.hasToken(),
  loading: false,
  error: null,
};

// Async thunks для работы с API
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials);
      const token = authDto.processAuthResponse(response);
      
      // Предполагаем, что бэкенд возвращает информацию о пользователе
      // вместе с токеном, или она может быть извлечена из JWT
      // Если это не так, можно вернуть заглушку и обновить данные позже
      return { 
        token, 
        user: {
          id: 0, // Будет обновлено при следующем запросе
          email: credentials.email,
          is_active: true,
          telegram_chat_id: null
        } 
      };
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Произошла неизвестная ошибка');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async ({ email, password }: RegisterCredentials, { rejectWithValue }) => {
    try {
      // Регистрация пользователя
      const user = await authApi.register({ email, password });
      
      // Сразу входим без отдельного запроса
      try {
        const response = await authApi.login({ email, password });
        const token = authDto.processAuthResponse(response);
        
        return { user, token };
      } catch (loginError) {
        // Если не удалось войти после регистрации, просто возвращаем пользователя
        // и перенаправляем на страницу входа
        console.error('Не удалось войти после регистрации:', loginError);
        return rejectWithValue('Регистрация успешна, но не удалось выполнить вход автоматически');
      }
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Произошла неизвестная ошибка');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      if (!authDto.hasToken()) {
        throw new Error('Не авторизован');
      }
      const user = await authApi.getCurrentUser();
      return user;
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Произошла неизвестная ошибка');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      authApi.logout();
      return true;
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Произошла неизвестная ошибка');
    }
  }
);

// Создаем Redux Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    resetAuth: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // Login reducers
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<{ token: string; user: User }>) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })
      
      // Register reducers
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action: PayloadAction<{ user: User; token: string }>) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Get current user reducers
      .addCase(getCurrentUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getCurrentUser.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        // Если получение пользователя не удалось, сбрасываем состояние
        state.isAuthenticated = false;
        state.token = null;
        localStorage.removeItem('token');
      })
      
      // Logout reducers
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      });
  },
});

export const { clearError, resetAuth } = authSlice.actions;
export default authSlice.reducer; 