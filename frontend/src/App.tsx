import { FC } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AppRoutes } from './routes';

export const App: FC = () => {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
};
