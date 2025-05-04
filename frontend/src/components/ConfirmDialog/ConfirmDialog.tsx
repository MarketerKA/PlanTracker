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
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
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
