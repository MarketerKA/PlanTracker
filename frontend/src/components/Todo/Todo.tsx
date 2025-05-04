import { FC, useState, useEffect } from 'react';
import styles from './Todo.module.scss';
import { TaskForm, TaskList, Timer } from '../../components';
import { useActivities } from '../../hooks/useActivities';
import { TaskType } from '../Task/types';
import { tagsApi, TagDto } from '../../api/tags';

export interface TodoProps {}

export const Todo: FC<TodoProps> = () => {
  const { 
    tasks, 
    loading, 
    error, 
    addTask, 
    toggleTaskComplete, 
    deleteTask,
    startTimer,
    pauseTimer,
    stopTimer,
    fetchTasks
  } = useActivities();

  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [availableTags, setAvailableTags] = useState<TagDto[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [tagsLoading, setTagsLoading] = useState(false);

  // Выбранная задача
  const selectedTask = tasks.find(task => task.id === selectedTaskId);

  // Загрузка тегов
  useEffect(() => {
    const loadTags = async () => {
      setTagsLoading(true);
      try {
        const tags = await tagsApi.getTags();
        setAvailableTags(tags);
      } catch (err) {
        console.error('Failed to load tags:', err);
      } finally {
        setTagsLoading(false);
      }
    };

    loadTags();
  }, []);

  // Обработчик добавления задачи
  const handleAddTask = async (task: Omit<TaskType, 'id'>) => {
    try {
      await addTask(task);
    } catch (err) {
      console.error('Error adding task:', err);
    }
  };

  // Обработчик изменения статуса выполнения задачи
  const handleToggleComplete = async (id: string) => {
    try {
      console.log(`Toggling task status ${id}...`);
      const task = tasks.find(t => t.id === id);
      console.log('Current task status:', task?.completed ? 'Completed' : 'Not completed');
      
      const result = await toggleTaskComplete(id);
      if (!result) {
        console.error('Failed to change task status');
      } else {
        console.log('Task status changed successfully');
      }
    } catch (err) {
      console.error('Error changing task status:', err);
    }
  };

  // Обработчик удаления задачи
  const handleDeleteTask = async (id: string) => {
    try {
      const result = await deleteTask(id);
      if (!result) {
        console.error('Failed to delete task');
      }
    } catch (err) {
      console.error('Error deleting task:', err);
    }
  };

  // Обработчик запуска таймера
  const handleTimerStart = async () => {
    if (selectedTaskId) {
      const success = await startTimer(selectedTaskId);
      if (success) setIsTimerRunning(true);
    }
  };

  // Обработчик паузы таймера
  const handleTimerPause = async () => {
    if (selectedTaskId) {
      const success = await pauseTimer(selectedTaskId);
      if (success) setIsTimerRunning(false);
    }
  };

  // Обработчик остановки таймера
  const handleTimerStop = async () => {
    if (selectedTaskId) {
      const success = await stopTimer(selectedTaskId);
      if (success) {
        setIsTimerRunning(false);
        await toggleTaskComplete(selectedTaskId);
        setSelectedTaskId(null);
      }
    }
  };

  // Обработчик выбора задачи
  const handleTaskSelect = (taskId: string) => {
    if (!isTimerRunning) {
      setSelectedTaskId(prevId => prevId === taskId ? null : taskId);
    }
  };

  // Обработчик выбора тега для фильтрации
  const handleTagSelect = (tag: string | null) => {
    setSelectedTag(tag);
    fetchTasks(0, 15, tag || undefined);
  };

  return (
    <div className={styles.todoWrapper}>
      {error && <div className={styles.errorMessage}>{error}</div>}
      
      <div className={styles.tagsFilter}>
        <h3 className={styles.filterTitle}>Filter by Tags</h3>
        <div className={styles.tagsList}>
          <button 
            className={`${styles.tagButton} ${selectedTag === null ? styles.active : ''}`}
            onClick={() => handleTagSelect(null)}
          >
            All Tasks
          </button>
          {tagsLoading ? (
            <div className={styles.tagsSkeleton}>Loading tags...</div>
          ) : (
            availableTags.map(tag => (
              <button 
                key={tag.id}
                className={`${styles.tagButton} ${selectedTag === tag.name ? styles.active : ''}`}
                onClick={() => handleTagSelect(tag.name)}
              >
                {tag.name}
              </button>
            ))
          )}
        </div>
      </div>
      
      <div className={styles.content}>
        <Timer 
          isRunning={isTimerRunning} 
          onStart={handleTimerStart} 
          onPause={handleTimerPause} 
          onStop={handleTimerStop}
          selectedTaskTitle={selectedTask?.title}
        />
        
        <TaskForm onAddTask={handleAddTask} />
        
        {loading ? (
          <div className={styles.loading}>Loading tasks...</div>
        ) : (
          <TaskList 
            tasks={tasks} 
            onToggleComplete={handleToggleComplete} 
            onDelete={handleDeleteTask}
            itemsPerPage={5}
            selectedTaskId={selectedTaskId}
            onTaskSelect={handleTaskSelect}
          />
        )}
      </div>
    </div>
  );
}; 