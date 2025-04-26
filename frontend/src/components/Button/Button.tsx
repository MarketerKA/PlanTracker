import { FC, ButtonHTMLAttributes } from 'react';
import styles from './Button.module.scss';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
}

const Button: FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  className, 
  ...props 
}) => {
  return (
    <button 
      className={`${styles.button} ${styles[variant]} ${className || ''}`} 
      {...props}
    >
      {children}
    </button>
  );
};

export default Button; 