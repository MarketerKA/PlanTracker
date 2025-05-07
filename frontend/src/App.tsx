import { FC, useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AppRoutes } from './routes';
import { store } from './redux/store';
import { getCurrentUser, authDto } from './redux/auth';

export const App: FC = () => {
  useEffect(() => {
    // If token exists, load user data
    if (authDto.hasToken()) {
      store.dispatch(getCurrentUser())
        .then(() => console.log('User loaded'))
        .catch(() => console.log('Error loading user'));
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
