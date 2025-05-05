import { FC } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import styles from './Header.module.scss';
import { Button } from '../Button';
import { ROUTES } from '../../routes';
import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import { logout } from '../../redux/auth';
import { RootState } from '../../redux/store';

// Using Record<string, never> instead of empty interface
type HeaderProps = Record<string, never>;

export const Header: FC<HeaderProps> = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
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
        <button
          className={styles.logo}
          onClick={() => navigate(ROUTES.HOME)}
          type="button"
        >
          <h1>Plan<span>Tracker</span></h1>
        </button>
        <nav className={styles.nav}>
          <ul>
            <li>
              <NavLink 
                to={ROUTES.TASKS} 
                className={({ isActive }) => isActive ? styles.active : ''}
              >
                Tasks
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
                Logout
              </Button>
            </>
          ) : (
            <Button 
              variant="secondary" 
              onClick={handleLoginClick}
            >
              Login
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}; 