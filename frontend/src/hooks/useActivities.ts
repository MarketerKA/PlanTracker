import { useState, useEffect, useCallback } from 'react';
import { activitiesApi, ActivityDto, ActivityCreateDto, ActivityUpdateDto, TimerActionDto } from '../api/activities';
import { TaskType } from '../components/Task/types';

// Converting ActivityDto to TaskType
const mapActivityToTask = (activity: ActivityDto): TaskType => {
  // Extract the due date from the description field if it exists
  let dueDate: string | undefined;
  
  if (activity.description && activity.description.startsWith("DUE_DATE:")) {
    dueDate = activity.description.split("DUE_DATE:")[1].trim();
    // Convert to datetime-local format (YYYY-MM-DDThh:mm)
    if (dueDate) {
      const date = new Date(dueDate);
      dueDate = date.toISOString().slice(0, 16);
    }
  } else {
    // Fallback to the current date and time
    dueDate = new Date().toISOString().slice(0, 16);
  }

  // Log for debugging
  console.log("API returned description:", activity.description);
  console.log("Final due date value:", dueDate);

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
  const dueDatePrefix = "DUE_DATE:";
  const dueDate = task.dueDate || new Date().toISOString().slice(0, 16);

  // scheduled_time в формате ISO (UTC)
  const scheduled_time = task.dueDate ? new Date(task.dueDate).toISOString() : undefined;

  return {
    title: task.title,
    description: `${dueDatePrefix}${dueDate}`,
    tags: task.tags || [],
    scheduled_time,
  };
};

// Converting TaskType to ActivityUpdateDto
const mapTaskToActivityUpdate = (task: Partial<TaskType>, originalTask?: TaskType): ActivityUpdateDto => {
  const updateDto: ActivityUpdateDto = {
    title: task.title ?? originalTask?.title ?? ""
  };

  if (task.tags !== undefined) updateDto.tags = task.tags;

  if (task.dueDate !== undefined) {
    const dueDatePrefix = "DUE_DATE:";
    updateDto.description = `${dueDatePrefix}${task.dueDate}`;
    // scheduled_time в формате ISO (UTC)
    updateDto.scheduled_time = task.dueDate ? new Date(task.dueDate).toISOString() : undefined;
  }

  if (task.completed !== undefined) {
    if (task.completed) {
      updateDto.end_time = new Date().toISOString();
    } else {
      updateDto.end_time = null;
    }
  }

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
      console.log("Task data received from form:", taskData);
      console.log("Selected due date from form:", taskData.dueDate);
      
      const activityData = mapTaskToActivityCreate(taskData);
      console.log("Data being sent to API:", activityData);
      
      const newActivity = await activitiesApi.createActivity(activityData);
      console.log("Response from API:", newActivity);
      
      const newTask = mapActivityToTask(newActivity);
      console.log("Task after mapping from response:", newTask);
      
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