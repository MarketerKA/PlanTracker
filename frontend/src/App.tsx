import { FC, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AppRoutes } from './routes';
import { store } from './redux/store';
import { getCurrentUser, authDto } from './redux/auth';

export const App: FC = () => {
  useEffect(() => {
    // Если есть токен, загружаем данные пользователя
    if (authDto.hasToken()) {
      store.dispatch(getCurrentUser())
        .then(() => console.log('Пользователь загружен'))
        .catch(() => console.log('Ошибка при загрузке пользователя'));
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
