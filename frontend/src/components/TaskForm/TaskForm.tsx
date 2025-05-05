import { FC, useState, FormEvent } from 'react';
import styles from './TaskForm.module.scss';
import { TaskType } from '../Task/types';

export interface TaskFormProps {
  onAddTask: (task: Omit<TaskType, 'id'>) => void;
}

export const TaskForm: FC<TaskFormProps> = ({ onAddTask }) => {
  const [title, setTitle] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) return;
    
    // Due date should be required, so don't submit if not provided
    if (!dueDate) return;
    
    const newTask: Omit<TaskType, 'id'> = {
      title: title.trim(),
      completed: false,
      tags,
      dueDate
    };
    
    onAddTask(newTask);
    
    // Reset form
    setTitle('');
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
          placeholder="Add new task..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={styles.input}
          onFocus={() => !isExpanded && setIsExpanded(true)}
          required
        />
      </div>
      
      {isExpanded && (
        <>
          <div className={styles.formRow}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Due Date (required)</label>
              <input
                type="datetime-local"
                value={dueDate}
                min={new Date().toISOString().slice(0, 16)}
                onChange={(e) => setDueDate(e.target.value)}
                className={styles.input}
                required
              />
            </div>
            
            <div className={styles.inputGroup}>
              <label className={styles.label} htmlFor="tag-input">Tags</label>
              <div className={styles.tagInput}>
                <input
                  id="tag-input"
                  type="text"
                  placeholder="Add tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  className={styles.input}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className={styles.addTagButton}
                  disabled={!newTag.trim()}
                >
                  +
                </button>
              </div>
              {tags.length > 0 && (
                <div className={styles.tagsContainer}>
                  {tags.map((tag) => (
                    <div key={tag} className={styles.tag}>
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className={styles.removeTagButton}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className={styles.formActions}>
            <button type="submit" className={styles.submitButton}>
              Add Task
            </button>
          </div>
        </>
      )}
    </form>
  );
};