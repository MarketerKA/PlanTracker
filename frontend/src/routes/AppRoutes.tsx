import { FC } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Login, Register, Tasks } from '../pages';
import { ROUTES } from './routeConstants';
import { ProtectedRoute } from './ProtectedRoute';

export const AppRoutes: FC = () => {
  return (
    <Routes>
      <Route 
        path={ROUTES.HOME} 
        element={
          <ProtectedRoute>
            <Tasks />
          </ProtectedRoute>
        } 
      />
      <Route path={ROUTES.LOGIN} element={<Login />} />
      <Route path={ROUTES.REGISTER} element={<Register />} />
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  );
}; 