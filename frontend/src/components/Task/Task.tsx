import { FC } from 'react';
import styles from './Task.module.scss';

export interface TaskType {
  id: string;
  title: string;
  completed: boolean;
  dueDate?: string;
  priority: 'low' | 'medium' | 'high';
}

export interface TaskProps {
  task: TaskType;
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
}

export const Task: FC<TaskProps> = ({ task, onToggleComplete, onDelete }) => {
  return (
    <div className={`${styles.task} ${task.completed ? styles.completed : ''}`}>
      <div className={styles.checkbox}>
        <input 
          type="checkbox" 
          checked={task.completed} 
          onChange={() => onToggleComplete(task.id)} 
        />
      </div>
      <div className={styles.content}>
        <div className={styles.title}>{task.title}</div>
        {task.dueDate && (
          <div className={styles.dueDate}>
            {new Date(task.dueDate).toLocaleDateString()}
          </div>
        )}
      </div>
      <div className={`${styles.priority} ${styles[task.priority]}`}>
        {task.priority}
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