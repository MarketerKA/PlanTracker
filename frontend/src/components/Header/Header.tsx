import { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Header.module.scss';
import { Button } from '../Button';
import { ROUTES } from '../../routes';

export interface HeaderProps {}

export const Header: FC<HeaderProps> = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate(ROUTES.LOGIN);
  };

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <h1>Plan<span>Tracker</span></h1>
        </div>
        <nav className={styles.nav}>
          <ul>
            <li><a href="#" className={styles.active}>Задачи</a></li>
          </ul>
        </nav>
        <div className={styles.actions}>
          <Button 
            variant="secondary" 
            onClick={handleLoginClick}
          >
            Войти
          </Button>
        </div>
      </div>
    </header>
  );
}; 