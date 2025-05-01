import { FC } from 'react';
import { useNavigate, NavLink, useLocation } from 'react-router-dom';
import styles from './Header.module.scss';
import { Button } from '../Button';
import { ROUTES } from '../../routes';
import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import { logout } from '../../redux/auth';
import { RootState } from '../../redux/store';

export interface HeaderProps {}

export const Header: FC<HeaderProps> = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  // @ts-ignore
  const { user, isAuthenticated } = useAppSelector((state: RootState) => state.auth);

  const handleLoginClick = () => {
    navigate(ROUTES.LOGIN);
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo} onClick={() => navigate(ROUTES.HOME)}>
          <h1>Plan<span>Tracker</span></h1>
        </div>
        <nav className={styles.nav}>
          <ul>
            <li>
              <NavLink 
                to={ROUTES.HOME} 
                className={({ isActive }) => isActive ? styles.active : ''}
              >
                Главная
              </NavLink>
            </li>
            <li>
              <NavLink 
                to={ROUTES.TASKS} 
                className={({ isActive }) => isActive ? styles.active : ''}
              >
                Задачи
              </NavLink>
            </li>
          </ul>
        </nav>
        <div className={styles.actions}>
          {isAuthenticated ? (
            <>
              <div className={styles.userEmail}>{user?.email}</div>
              <Button 
                variant="secondary" 
                onClick={handleLogout}
              >
                Выйти
              </Button>
            </>
          ) : (
            <Button 
              variant="secondary" 
              onClick={handleLoginClick}
            >
              Войти
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}; 