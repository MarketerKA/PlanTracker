import { useState, useEffect, useCallback } from 'react';
import { activitiesApi, ActivityDto, ActivityCreateDto, ActivityUpdateDto, TimerActionDto } from '../api/activities';
import { TaskType } from '../components/Task/types';

// Преобразование ActivityDto в TaskType
const mapActivityToTask = (activity: ActivityDto): TaskType => {
  // Функция для безопасного форматирования даты
  const formatDate = (dateString?: string | null): string | undefined => {
    if (!dateString) return undefined;
    try {
      return new Date(dateString).toISOString().split('T')[0];
    } catch (err) {
      console.error(`Ошибка при форматировании даты ${dateString}:`, err);
      return undefined;
    }
  };

  return {
    id: activity.id.toString(),
    title: activity.title,
    completed: Boolean(activity.end_time),  // Если есть end_time, считаем задачу завершенной
    tags: activity.tags.map(tag => tag.name),
    dueDate: formatDate(activity.end_time),
    description: activity.description,
    recordedTime: activity.recorded_time,
    timerStatus: activity.timer_status,
  };
};

// Преобразование TaskType в ActivityCreateDto
const mapTaskToActivityCreate = (task: Omit<TaskType, 'id'>): ActivityCreateDto => {
  return {
    title: task.title,
    description: task.description || null,
    tags: task.tags || [],
  };
};

// Преобразование TaskType в ActivityUpdateDto
const mapTaskToActivityUpdate = (task: Partial<TaskType>, originalTask?: TaskType): ActivityUpdateDto => {
  // Задача может быть частичной (только изменяемые поля),
  // поэтому нам нужен оригинальный объект задачи, чтобы получить недостающие данные
  const updateDto: ActivityUpdateDto = {
    // Обязательное поле title всегда должно присутствовать
    title: task.title ?? originalTask?.title ?? ""
  };
  
  // Добавляем остальные поля, если они есть
  if (task.description !== undefined) updateDto.description = task.description;
  if (task.tags !== undefined) updateDto.tags = task.tags;
  
  // Обработка статуса выполнения
  if (task.completed !== undefined) {
    if (task.completed) {
      // Для завершенной задачи устанавливаем текущую дату в ISO формате
      updateDto.end_time = new Date().toISOString();
    } else {
      // Для незавершенной задачи устанавливаем null
      updateDto.end_time = null;
    }
  }
  
  // Добавление других полей, если они есть
  if (task.recordedTime !== undefined) updateDto.recorded_time = task.recordedTime;
  if (task.timerStatus !== undefined) updateDto.timer_status = task.timerStatus;
  
  return updateDto;
};

export const useActivities = () => {
  const [tasks, setTasks] = useState<TaskType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Загрузка задач
  const fetchTasks = useCallback(async (skip = 0, limit = 15, tag?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activities = await activitiesApi.getActivities(skip, limit, tag);
      const mappedTasks = activities.map(mapActivityToTask);
      setTasks(mappedTasks);
    } catch (err) {
      setError('Не удалось загрузить задачи');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Загрузка задач при монтировании
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Добавление новой задачи
  const addTask = async (taskData: Omit<TaskType, 'id'>) => {
    setLoading(true);
    setError(null);
    
    try {
      const activityData = mapTaskToActivityCreate(taskData);
      const newActivity = await activitiesApi.createActivity(activityData);
      const newTask = mapActivityToTask(newActivity);
      
      setTasks(prev => [newTask, ...prev]);
      return newTask;
    } catch (err) {
      setError('Не удалось создать задачу');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Обновление задачи
  const updateTask = async (id: string, taskData: Partial<TaskType>) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Обновление задачи ${id} с данными:`, taskData);
      
      const activityId = parseInt(id);
      if (isNaN(activityId)) {
        throw new Error(`Некорректный ID задачи: ${id}`);
      }
      
      // Найдем оригинальную задачу
      const originalTask = tasks.find(task => task.id === id);
      if (!originalTask) {
        throw new Error(`Задача с ID ${id} не найдена в списке`);
      }
      
      const updateData = mapTaskToActivityUpdate(taskData, originalTask);
      console.log('Преобразованные данные для API:', updateData);
      
      const updatedActivity = await activitiesApi.updateActivity(activityId, updateData);
      console.log('Ответ API:', updatedActivity);
      
      const updatedTask = mapActivityToTask(updatedActivity);
      
      setTasks(prev => 
        prev.map(task => task.id === id ? updatedTask : task)
      );
      
      return updatedTask;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
      console.error(`Ошибка при обновлении задачи ${id}:`, err);
      setError(`Не удалось обновить задачу: ${errorMessage}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Удаление задачи
  const deleteTask = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activityId = parseInt(id);
      await activitiesApi.deleteActivity(activityId);
      
      setTasks(prev => prev.filter(task => task.id !== id));
      return true;
    } catch (err) {
      setError('Не удалось удалить задачу');
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Изменение статуса выполнения задачи
  const toggleTaskComplete = async (id: string) => {
    const task = tasks.find(t => t.id === id);
    if (!task) {
      console.error(`Задача с ID ${id} не найдена`);
      return false;
    }
    
    try {
      console.log(`Изменение статуса задачи ${id} с ${task.completed} на ${!task.completed}`);
      
      // Подготавливаем данные для обновления - только статус выполнения
      const updateData: Partial<TaskType> = { completed: !task.completed };
      
      const updatedTask = await updateTask(id, updateData);
      return Boolean(updatedTask);
    } catch (err) {
      console.error(`Ошибка при изменении статуса задачи ${id}:`, err);
      return false;
    }
  };

  // Управление таймером
  const startTimer = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activityId = parseInt(id);
      const timerAction: TimerActionDto = { action: 'start' };
      
      const updatedActivity = await activitiesApi.timerAction(activityId, timerAction);
      const updatedTask = mapActivityToTask(updatedActivity);
      
      setTasks(prev => 
        prev.map(task => task.id === id ? updatedTask : task)
      );
      
      return true;
    } catch (err) {
      setError('Не удалось запустить таймер');
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const pauseTimer = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activityId = parseInt(id);
      const timerAction: TimerActionDto = { action: 'pause' };
      
      const updatedActivity = await activitiesApi.timerAction(activityId, timerAction);
      const updatedTask = mapActivityToTask(updatedActivity);
      
      setTasks(prev => 
        prev.map(task => task.id === id ? updatedTask : task)
      );
      
      return true;
    } catch (err) {
      setError('Не удалось приостановить таймер');
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const stopTimer = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activityId = parseInt(id);
      const timerAction: TimerActionDto = { action: 'stop' };
      
      const updatedActivity = await activitiesApi.timerAction(activityId, timerAction);
      const updatedTask = mapActivityToTask(updatedActivity);
      
      setTasks(prev => 
        prev.map(task => task.id === id ? updatedTask : task)
      );
      
      return true;
    } catch (err) {
      setError('Не удалось остановить таймер');
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    addTask,
    updateTask,
    deleteTask,
    toggleTaskComplete,
    startTimer,
    pauseTimer,
    stopTimer
  };
}; 