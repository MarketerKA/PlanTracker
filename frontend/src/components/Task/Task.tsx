import { FC } from 'react';
import { TaskType } from './types';
import styles from './Task.module.scss';

export interface TaskProps {
  task: TaskType;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  isSelected?: boolean;
  onSelect?: () => void;
}

// Функция для форматирования времени в формат ЧЧ:ММ:СС
const formatTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  return [
    hours.toString().padStart(2, '0'),
    minutes.toString().padStart(2, '0'),
    secs.toString().padStart(2, '0')
  ].join(':');
};

export const Task: FC<TaskProps> = ({ 
  task, 
  onToggleComplete, 
  onDelete,
  isSelected,
  onSelect
}) => {
  // Иконка статуса таймера
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

  return (
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
        
        {task.description && (
          <div className={styles.description}>{task.description}</div>
        )}
        
        <div className={styles.details}>
          {task.dueDate && (
            <div className={styles.dueDate}>
              {new Date(task.dueDate).toLocaleDateString()}
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
        onClick={(e) => {
          e.stopPropagation();
          onDelete(task.id);
        }}
      >
        ✕
      </button>
    </div>
  );
};