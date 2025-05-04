import { configureStore } from '@reduxjs/toolkit';
import authReducer from './auth';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    // add other reducers here as needed
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// Types for use in components
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 