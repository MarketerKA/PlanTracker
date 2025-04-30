import { configureStore } from '@reduxjs/toolkit';
import authReducer from './auth';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    // здесь можно добавить другие редьюсеры по мере необходимости
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// Типы для использования в компонентах
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 