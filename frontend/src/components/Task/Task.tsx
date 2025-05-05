import { FC, useState } from 'react';
import { TaskType } from './types';
import styles from './Task.module.scss';
import { ConfirmDialog } from '../ConfirmDialog';

export interface TaskProps {
  task: TaskType;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  isSelected?: boolean;
  onSelect?: () => void;
}

// Function to format time (XX:XX:XX)
const formatTime = (seconds: number): string => {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  return [hrs, mins, secs]
    .map(val => val.toString().padStart(2, '0'))
    .join(':');
};

export const Task: FC<TaskProps> = ({ 
  task, 
  onToggleComplete, 
  onDelete,
  isSelected,
  onSelect
}) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Timer status icon
  const renderTimerStatus = () => {
    if (!task.timerStatus) return null;
    
    switch (task.timerStatus) {
      case 'running':
        return <span className={`${styles.timerStatus} ${styles.running}`}>▶</span>;
      case 'paused':
        return <span className={`${styles.timerStatus} ${styles.paused}`}>⏸</span>;
      default:
        return null;
    }
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteConfirm(true);
  };

  return (
    <>
      <div 
        className={`${styles.task} ${task.completed ? styles.completed : ''} ${isSelected ? styles.selected : ''}`}
        onClick={onSelect}
      >
        <div className={styles.checkbox}>
          <input 
            type="checkbox" 
            checked={task.completed} 
            onChange={(e) => {
              e.stopPropagation();
              onToggleComplete(task.id);
            }} 
          />
        </div>
        <div className={styles.content}>
          <div className={styles.header}>
            <div className={styles.title}>
              {task.title}
              {renderTimerStatus()}
            </div>
            {task.recordedTime !== undefined && task.recordedTime > 0 && (
              <div className={styles.recordedTime}>
                {formatTime(task.recordedTime)}
              </div>
            )}
          </div>
          
          <div className={styles.details}>
            {task.dueDate && (
              <div className={styles.dueDate}>
                {new Date(task.dueDate).toLocaleString(undefined, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            )}
            {task.tags.length > 0 && (
              <div className={styles.tags}>
                {task.tags.map(tag => (
                  <span key={tag} className={styles.tag}>
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
        <button 
          className={styles.deleteBtn}
          onClick={handleDeleteClick}
        >
          ✕
        </button>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete task?"
        message={`Are you sure you want to delete the task "${task.title}"? This action cannot be undone.`}
        confirmText="Delete"
        onConfirm={() => {
          onDelete(task.id);
          setShowDeleteConfirm(false);
        }}
        onCancel={() => setShowDeleteConfirm(false)}
        variant="danger"
      />
    </>
  );
};