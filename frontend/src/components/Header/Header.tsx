import { FC } from 'react';
import styles from './Header.module.scss';
import Button from '../Button';

const Header: FC = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <h1>Plan<span>Treker</span></h1>
        </div>
        <nav className={styles.nav}>
          <ul>
            <li><a href="#" className={styles.active}>Главная</a></li>
            <li><a href="#">Задачи</a></li>
            <li><a href="#">Таймер</a></li>
            <li><a href="#">Отчеты</a></li>
          </ul>
        </nav>
        <div className={styles.actions}>
          <Button variant="secondary">Войти</Button>
        </div>
      </div>
    </header>
  );
};

export default Header; 