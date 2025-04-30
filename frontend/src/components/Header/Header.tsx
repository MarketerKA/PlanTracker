import { FC } from 'react';
import styles from './Header.module.scss';

export interface HeaderProps {}

export const Header: FC<HeaderProps> = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <h1>Plan<span>Treker</span></h1>
        </div>
        <nav className={styles.nav}>
          <ul>
            <li><a href="#" className={styles.active}>Задачи</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
}; 