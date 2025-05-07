import { FC, useState, useEffect, useRef } from 'react';
import styles from './Todo.module.scss';
import { TaskForm, TaskList, Timer } from '../../components';
import { useActivities } from '../../hooks/useActivities';
import { TaskType } from '../Task/types';
import { tagsApi, TagDto } from '../../api/tags';

// Using Record<string, never> instead of empty interface
type TodoProps = Record<string, never>;

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

  // Track if initial task restoration has been done
  const initializedRef = useRef(false);

  // Initialize selected task from localStorage if available
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(() => {
    const savedTaskId = localStorage.getItem('selectedTaskId');
    return savedTaskId || null;
  });
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [availableTags, setAvailableTags] = useState<TagDto[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [tagsLoading, setTagsLoading] = useState(false);

  // Save selected task ID to localStorage whenever it changes
  useEffect(() => {
    if (selectedTaskId) {
      localStorage.setItem('selectedTaskId', selectedTaskId);
    } else {
      localStorage.removeItem('selectedTaskId');
    }
  }, [selectedTaskId]);

  // Filtered and sorted tasks based on selected date
  const filteredTasks = tasks
    .filter(task => {
      // If no date selected, show all tasks
      if (!selectedDate) return true;
      
      // Only show tasks with a due date
      if (!task.dueDate) return false;
      
      // Compare dates by converting both to YYYY-MM-DD format
      // Handle both date and datetime strings
      const taskDate = new Date(task.dueDate).toISOString().split('T')[0];
      
      return taskDate === selectedDate;
    })
    .sort((a, b) => {
      // Sort by date if dates are available
      if (a.dueDate && b.dueDate) {
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
      }
      
      // If one task has a date and the other doesn't, prioritize the one with a date
      if (a.dueDate && !b.dueDate) return -1;
      if (!a.dueDate && b.dueDate) return 1;
      
      // Default sort by completion status (incomplete first)
      return a.completed === b.completed ? 0 : a.completed ? 1 : -1;
    });

  // Selected task
  const selectedTask = tasks.find(task => task.id === selectedTaskId);

  // Keep timer running state in sync with selected task
  useEffect(() => {
    if (selectedTask) {
      setIsTimerRunning(selectedTask.timerStatus === 'running');
    }
  }, [selectedTask]);

  // Force refresh tasks on component mount to ensure fresh timer data
  useEffect(() => {
    // Only perform the initialization once
    if (initializedRef.current) return;
    
    // Refresh tasks on mount to get the most up-to-date timer data
    const refreshData = async () => {
      await fetchTasks();
      
      // After tasks are loaded, check if we have a saved task ID
      const savedTaskId = localStorage.getItem('selectedTaskId');
      if (savedTaskId && tasks.length > 0) {
        // Find the task in the loaded tasks
        const savedTask = tasks.find(task => task.id === savedTaskId);
        if (savedTask) {
          // If the task is found, restore its selection
          setSelectedTaskId(savedTaskId);
          // Set the timer running state based on the saved task's status
          setIsTimerRunning(savedTask.timerStatus === 'running');
        } else {
          // If the saved task is not found (maybe deleted), clear localStorage
          localStorage.removeItem('selectedTaskId');
        }
      }
      
      initializedRef.current = true;
    };
    
    refreshData();
  }, [fetchTasks, tasks]);

  // Loading tags
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

  // Task add handler
  const handleAddTask = async (task: Omit<TaskType, 'id'>) => {
    try {
      await addTask(task);
    } catch (err) {
      console.error('Error adding task:', err);
    }
  };

  // Task completion status change handler
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

  // Task delete handler
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

  // Timer start handler
  const handleTimerStart = async () => {
    if (selectedTaskId) {
      const success = await startTimer(selectedTaskId);
      if (success) setIsTimerRunning(true);
    }
  };

  // Timer pause handler
  const handleTimerPause = async () => {
    if (selectedTaskId) {
      const success = await pauseTimer(selectedTaskId);
      if (success) setIsTimerRunning(false);
    }
  };

  // Timer stop handler
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

  // Task selection handler
  const handleTaskSelect = (taskId: string) => {
    if (!isTimerRunning) {
      const newSelectedTaskId = selectedTaskId === taskId ? null : taskId;
      setSelectedTaskId(newSelectedTaskId);
      
      // Update timer running state based on the selected task's timer status
      if (newSelectedTaskId) {
        const task = tasks.find(t => t.id === newSelectedTaskId);
        setIsTimerRunning(task?.timerStatus === 'running');
      } else {
        setIsTimerRunning(false);
      }
    }
  };

  // Tag selection handler for filtering
  const handleTagSelect = (tag: string | null) => {
    setSelectedTag(tag);
    fetchTasks(0, 15, tag || undefined);
  };

  // Date selection handler for filtering
  const handleDateSelect = (date: string) => {
    // If date is empty string, clear the filter
    if (!date) {
      setSelectedDate('');
      return;
    }
    
    // Ensure date is in YYYY-MM-DD format
    const formattedDate = date.split('T')[0];
    setSelectedDate(formattedDate);
  };

  // Reset all filters
  const handleResetFilters = () => {
    setSelectedTag(null);
    setSelectedDate('');
    fetchTasks(0, 15);
  };

  return (
    <div className={styles.todoWrapper}>
      {error && <div className={styles.errorMessage}>{error}</div>}
      
      <div className={styles.content}>
        <Timer 
          isRunning={isTimerRunning} 
          onStart={handleTimerStart} 
          onPause={handleTimerPause} 
          onStop={handleTimerStop}
          selectedTaskTitle={selectedTask?.title}
          recordedTime={selectedTask?.recordedTime}
          lastTimerStart={selectedTask?.lastTimerStart}
        />
        
        <TaskForm onAddTask={handleAddTask} />
        
        <div className={styles.filters}>
          <div className={styles.filterRow}>
            <div className={styles.filterSection}>
              <label className={styles.filterLabel}>Date:</label>
              <div className={styles.dateFilter}>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => handleDateSelect(e.target.value)}
                  className={styles.dateInput}
                  aria-label="Filter tasks by date"
                />
                {selectedDate && (
                  <button 
                    className={styles.clearButton}
                    onClick={() => setSelectedDate('')}
                    aria-label="Clear date filter"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            
            <div className={styles.filterSection}>
              <label className={styles.filterLabel}>Tags:</label>
              <div className={styles.tagsList}>
                <button 
                  className={`${styles.tagButton} ${selectedTag === null ? styles.active : ''}`}
                  onClick={() => handleTagSelect(null)}
                >
                  All
                </button>
                {tagsLoading ? (
                  <span className={styles.tagsSkeleton}>Loading...</span>
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
            
            {(selectedTag || selectedDate) && (
              <button 
                className={styles.resetButton}
                onClick={handleResetFilters}
              >
                Reset
              </button>
            )}
          </div>
        </div>
        
        {loading ? (
          <div className={styles.loading}>Loading tasks...</div>
        ) : (
          <TaskList 
            tasks={filteredTasks} 
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