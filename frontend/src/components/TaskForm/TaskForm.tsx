import { FC, useState, FormEvent } from 'react';
import styles from './TaskForm.module.scss';
import { TaskType } from '../Task/types';

export interface TaskFormProps {
  onAddTask: (task: Omit<TaskType, 'id'>) => void;
}

export const TaskForm: FC<TaskFormProps> = ({ onAddTask }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) return;
    
    const newTask: Omit<TaskType, 'id'> = {
      title: title.trim(),
      completed: false,
      tags,
      ...(dueDate && { dueDate }),
      ...(description.trim() && { description: description.trim() })
    };
    
    onAddTask(newTask);
    
    // Сброс формы
    setTitle('');
    setDescription('');
    setDueDate('');
    setTags([]);
    setNewTag('');
    setIsExpanded(false);
  };

  const handleAddTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
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
          onFocus={() => !isExpanded && setIsExpanded(true)}
          required
        />
      </div>
      
      {isExpanded && (
        <>
          <div className={styles.inputGroup}>
            <textarea
              placeholder="Описание задачи (необязательно)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className={`${styles.input} ${styles.textarea}`}
              rows={3}
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
              <label className={styles.label}>Теги</label>
              <div className={styles.tagsInput}>
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                  placeholder="Введите тег..."
                  className={styles.input}
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className={styles.addTagButton}
                >
                  +
                </button>
              </div>
              <div className={styles.tagsList}>
                {tags.map(tag => (
                  <span key={tag} className={styles.tag}>
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className={styles.removeTag}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
      
      <button type="submit" className={styles.submitButton}>
        Добавить задачу
      </button>
    </form>
  );
};