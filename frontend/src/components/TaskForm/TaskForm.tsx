import { FC, useState, FormEvent } from 'react';
import styles from './TaskForm.module.scss';
import { TaskType } from '../Task';

interface TaskFormProps {
  onAddTask: (task: Omit<TaskType, 'id'>) => void;
}

const TaskForm: FC<TaskFormProps> = ({ onAddTask }) => {
  const [title, setTitle] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<TaskType['priority']>('medium');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) return;
    
    const newTask: Omit<TaskType, 'id'> = {
      title: title.trim(),
      completed: false,
      priority,
      ...(dueDate && { dueDate })
    };
    
    onAddTask(newTask);
    
    // Сброс формы
    setTitle('');
    setDueDate('');
    setPriority('medium');
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.inputGroup}>
        <input
          type="text"
          placeholder="Добавить новую задачу..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={styles.input}
          required
        />
      </div>
      
      <div className={styles.formRow}>
        <div className={styles.inputGroup}>
          <label className={styles.label}>Срок</label>
          <input
            type="date"
            value={dueDate}
            min={new Date().toISOString().split('T')[0]}
            onChange={(e) => setDueDate(e.target.value)}
            className={styles.input}
          />
        </div>
        
        <div className={styles.inputGroup}>
          <label className={styles.label}>Приоритет</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskType['priority'])}
            className={styles.select}
          >
            <option value="low">Низкий</option>
            <option value="medium">Средний</option>
            <option value="high">Высокий</option>
          </select>
        </div>
      </div>
      
      <button type="submit" className={styles.submitButton}>
        Добавить задачу
      </button>
    </form>
  );
};

export default TaskForm; 