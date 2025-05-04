import { FC, ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '../redux/hooks';
import { ROUTES } from './routeConstants';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute: FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAppSelector(state => state.auth);
  
  // If checking authentication, show loading indicator
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: 'calc(100vh - 70px)', // Account for header height
        color: 'var(--text-primary)'
      }}>
        Loading...
      </div>
    );
  }
  
  // If not authenticated, redirect to login page
  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }
  
  // If authenticated, show the requested component
  return <>{children}</>;
}; 