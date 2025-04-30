import { FC, useState, InputHTMLAttributes, ReactNode } from 'react';
import styles from './InputField.module.scss';

export interface InputFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'className'> {
  label: string;
  error?: string;
  icon?: ReactNode;
  rightIcon?: ReactNode;
  onRightIconClick?: () => void;
}

export const InputField: FC<InputFieldProps> = ({
  label,
  error,
  icon,
  rightIcon,
  onRightIconClick,
  type = 'text',
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    if (props.onBlur) {
      props.onBlur(e);
    }
  };

  return (
    <div className={styles.inputContainer}>
      <label className={styles.label}>{label}</label>
      <div 
        className={`${styles.inputWrapper} ${isFocused ? styles.focused : ''} ${error ? styles.error : ''}`}
      >
        {icon && <div className={styles.iconLeft}>{icon}</div>}
        <input
          className={styles.input}
          type={type}
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...props}
        />
        {rightIcon && (
          <div 
            className={styles.iconRight} 
            onClick={onRightIconClick}
          >
            {rightIcon}
          </div>
        )}
      </div>
      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
}; 