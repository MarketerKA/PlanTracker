import { FC, ReactNode } from 'react';
import styles from './AuthLayout.module.scss';

export interface AuthLayoutProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export const AuthLayout: FC<AuthLayoutProps> = ({ title, subtitle, children }) => {
  return (
    <div className={styles.authLayout}>
      <div className={styles.authContainer}>
        <div className={styles.header}>
          <h1 className={styles.title}>{title}</h1>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>
  );
}; 