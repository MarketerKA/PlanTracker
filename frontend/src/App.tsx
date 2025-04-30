import { FC, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AppRoutes } from './routes';
import { store } from './redux/store';
import { getCurrentUser } from './redux/auth';

export const App: FC = () => {
  useEffect(() => {
    // Проверяем, есть ли токен и нет ли данных пользователя
    const { auth } = store.getState();
    if (auth.token && !auth.user?.id) {
      // Загружаем данные пользователя только если есть токен, но нет ID пользователя
      store.dispatch(getCurrentUser());
    }
  }, []);

  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </Provider>
  );
};
