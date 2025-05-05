import { useState, useEffect, useCallback } from 'react';
import { activitiesApi, ActivityDto, ActivityCreateDto, ActivityUpdateDto, TimerActionDto } from '../api/activities';
import { TaskType } from '../components/Task/types';

// Converting ActivityDto to TaskType
const mapActivityToTask = (activity: ActivityDto): TaskType => {
  // Function for safely formatting date
  const formatDate = (dateString?: string | null): string | undefined => {
    if (!dateString) return undefined;
    try {
      return new Date(dateString).toISOString().split('T')[0];
    } catch (err) {
      console.error(`Error formatting date ${dateString}:`, err);
      return undefined;
    }
  };

  // Get due date from due_date field if exists, otherwise use end_time
  let dueDate = formatDate(activity.due_date) || formatDate(activity.end_time);
  
  // If no due date is set, use today's date as fallback
  if (!dueDate) {
    dueDate = new Date().toISOString().split('T')[0];
  }

  return {
    id: activity.id.toString(),
    title: activity.title,
    completed: Boolean(activity.end_time),  // If end_time exists, consider the task completed
    tags: activity.tags.map(tag => tag.name),
    dueDate,
    recordedTime: activity.recorded_time,
    timerStatus: activity.timer_status,
  };
};

// Converting TaskType to ActivityCreateDto
const mapTaskToActivityCreate = (task: Omit<TaskType, 'id'>): ActivityCreateDto => {
  return {
    title: task.title,
    tags: task.tags || [],
    due_date: task.dueDate || new Date().toISOString().split('T')[0],
  };
};

// Converting TaskType to ActivityUpdateDto
const mapTaskToActivityUpdate = (task: Partial<TaskType>, originalTask?: TaskType): ActivityUpdateDto => {
  // The task can be partial (only changeable fields),
  // so we need the original task object to get the missing data
  const updateDto: ActivityUpdateDto = {
    // Required field title must always be present
    title: task.title ?? originalTask?.title ?? ""
  };
  
  // Add remaining fields if they exist
  if (task.tags !== undefined) updateDto.tags = task.tags;
  
  // Handling due date
  if (task.dueDate !== undefined) {
    updateDto.due_date = task.dueDate;
  }
  
  // Processing completion status
  if (task.completed !== undefined) {
    if (task.completed) {
      // For completed task, set current date in ISO format
      updateDto.end_time = new Date().toISOString();
    } else {
      // For incomplete task, set null
      updateDto.end_time = null;
    }
  }
  
  // Adding other fields if they exist
  if (task.recordedTime !== undefined) updateDto.recorded_time = task.recordedTime;
  if (task.timerStatus !== undefined) updateDto.timer_status = task.timerStatus;
  
  return updateDto;
};

export const useActivities = () => {
  const [tasks, setTasks] = useState<TaskType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Loading tasks
  const fetchTasks = useCallback(async (skip = 0, limit = 15, tag?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activities = await activitiesApi.getActivities(skip, limit, tag);
      const mappedTasks = activities.map(mapActivityToTask);
      setTasks(mappedTasks);
    } catch (err) {
      setError('Failed to load tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Loading tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Adding a new task
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
      setError('Failed to create task');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Updating a task
  const updateTask = async (id: string, taskData: Partial<TaskType>) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Updating task ${id} with data:`, taskData);
      
      const activityId = parseInt(id);
      if (isNaN(activityId)) {
        throw new Error(`Invalid task ID: ${id}`);
      }
      
      // Find the original task
      const originalTask = tasks.find(task => task.id === id);
      if (!originalTask) {
        throw new Error(`Task with ID ${id} not found in the list`);
      }
      
      const updateData = mapTaskToActivityUpdate(taskData, originalTask);
      console.log('Transformed data for API:', updateData);
      
      const updatedActivity = await activitiesApi.updateActivity(activityId, updateData);
      console.log('API response:', updatedActivity);
      
      const updatedTask = mapActivityToTask(updatedActivity);
      
      setTasks(prev => 
        prev.map(task => task.id === id ? updatedTask : task)
      );
      
      return updatedTask;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error(`Error updating task ${id}:`, err);
      setError(`Failed to update task: ${errorMessage}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Deleting a task
  const deleteTask = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const activityId = parseInt(id);
      await activitiesApi.deleteActivity(activityId);
      
      setTasks(prev => prev.filter(task => task.id !== id));
      return true;
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Changing task completion status
  const toggleTaskComplete = async (id: string) => {
    const task = tasks.find(t => t.id === id);
    if (!task) {
      console.error(`Task with ID ${id} not found`);
      return false;
    }
    
    try {
      console.log(`Changing task status ${id} from ${task.completed} to ${!task.completed}`);
      
      // Prepare data for update - only completion status
      const updateData: Partial<TaskType> = { completed: !task.completed };
      
      const updatedTask = await updateTask(id, updateData);
      return Boolean(updatedTask);
    } catch (err) {
      console.error(`Error changing task status ${id}:`, err);
      return false;
    }
  };

  // Timer management
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
      setError('Failed to start timer');
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
      setError('Failed to pause timer');
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
      setError('Failed to stop timer');
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