import { FC, ButtonHTMLAttributes } from 'react';
import styles from './Button.module.scss';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
}

export const Button: FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  className, 
  ...props 
}) => {
  return (
    <button 
      className={`${styles.button} ${styles[variant]} ${className ?? ''}`} 
      {...props}
    >
      {children}
    </button>
  );
}; 