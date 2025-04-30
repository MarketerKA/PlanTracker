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

export const Task: FC<TaskProps> = ({ 
  task, 
  onToggleComplete, 
  onDelete,
  isSelected,
  onSelect
}) => {
  return (
    <div 
      className={`${styles.task} ${task.completed ? styles.completed : ''} ${isSelected ? styles.selected : ''}`}
      onClick={onSelect}
    >
      <div className={styles.checkbox}>
        <input 
          type="checkbox" 
          checked={task.completed} 
          onChange={() => onToggleComplete(task.id)} 
        />
      </div>
      <div className={styles.content}>
        <div className={styles.title}>{task.title}</div>
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
        onClick={() => onDelete(task.id)}
      >
        ✕
      </button>
    </div>
  );
};