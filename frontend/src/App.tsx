import { FC, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AppRoutes } from './routes';
import { store } from './redux/store';
import { getCurrentUser } from './redux/auth';

export const App: FC = () => {
  useEffect(() => {
    // Пытаемся получить данные пользователя если есть токен
    store.dispatch(getCurrentUser());
  }, []);

  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </Provider>
  );
};
