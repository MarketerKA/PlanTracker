import { FC } from 'react';
import styles from './ConfirmDialog.module.scss';
import { Button } from '../Button';

export interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'warning' | 'danger' | 'info';
}

export const ConfirmDialog: FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  onConfirm,
  onCancel,
  variant = 'info'
}) => {
  if (!isOpen) return null;

  return (
    <div className={styles.overlay}>
      <div className={`${styles.dialog} ${styles[variant]}`}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.message}>{message}</p>
        <div className={styles.actions}>
          <Button 
            variant="secondary" 
            onClick={onCancel}
          >
            {cancelText}
          </Button>
          <Button 
            onClick={onConfirm}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
};
