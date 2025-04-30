import { FC } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Home, Login, Register } from '../pages';
import { ROUTES } from './routeConstants';

export const AppRoutes: FC = () => {
  return (
    <Routes>
      <Route path={ROUTES.HOME} element={<Home />} />
      <Route path={ROUTES.LOGIN} element={<Login />} />
      <Route path={ROUTES.REGISTER} element={<Register />} />
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  );
}; 