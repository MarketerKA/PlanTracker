import { FC, ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '../redux/hooks';
import { ROUTES } from './routeConstants';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute: FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAppSelector(state => state.auth);
  
  // Если проверяем аутентификацию, показываем индикатор загрузки
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: 'calc(100vh - 70px)', // Учитываем высоту хедера
        color: 'var(--text-primary)'
      }}>
        Загрузка...
      </div>
    );
  }
  
  // Если не авторизован, перенаправляем на страницу входа
  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }
  
  // Если авторизован, показываем запрошенный компонент
  return <>{children}</>;
}; 