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
        console.error('Не удалось загрузить теги:', err);
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
      console.error('Ошибка при добавлении задачи:', err);
    }
  };

  // Обработчик изменения статуса выполнения задачи
  const handleToggleComplete = async (id: string) => {
    try {
      console.log(`Переключение статуса задачи ${id}...`);
      const task = tasks.find(t => t.id === id);
      console.log('Текущий статус задачи:', task?.completed ? 'Выполнена' : 'Не выполнена');
      
      const result = await toggleTaskComplete(id);
      if (!result) {
        console.error('Не удалось изменить статус задачи');
      } else {
        console.log('Статус задачи успешно изменен');
      }
    } catch (err) {
      console.error('Ошибка при изменении статуса задачи:', err);
    }
  };

  // Обработчик удаления задачи
  const handleDeleteTask = async (id: string) => {
    try {
      const result = await deleteTask(id);
      if (!result) {
        console.error('Не удалось удалить задачу');
      }
    } catch (err) {
      console.error('Ошибка при удалении задачи:', err);
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
        <h3 className={styles.filterTitle}>Фильтр по тегам</h3>
        <div className={styles.tagsList}>
          <button 
            className={`${styles.tagButton} ${selectedTag === null ? styles.active : ''}`}
            onClick={() => handleTagSelect(null)}
          >
            Все задачи
          </button>
          {tagsLoading ? (
            <div className={styles.tagsSkeleton}>Загрузка тегов...</div>
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
          <div className={styles.loading}>Загрузка задач...</div>
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