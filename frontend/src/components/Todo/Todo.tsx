import { FC, useState, useEffect } from 'react';
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

  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [availableTags, setAvailableTags] = useState<TagDto[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [tagsLoading, setTagsLoading] = useState(false);

  // Filtered tasks based on selected date
  const filteredTasks = tasks.filter(task => {
    // If no date selected, show all tasks
    if (!selectedDate) return true;
    
    // Only show tasks with a due date that matches the selected date
    return task.dueDate === selectedDate;
  });

  // Selected task
  const selectedTask = tasks.find(task => task.id === selectedTaskId);

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
      setSelectedTaskId(prevId => prevId === taskId ? null : taskId);
    }
  };

  // Tag selection handler for filtering
  const handleTagSelect = (tag: string | null) => {
    setSelectedTag(tag);
    fetchTasks(0, 15, tag || undefined);
  };

  // Date selection handler for filtering
  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
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
                />
                {selectedDate && (
                  <button 
                    className={styles.clearButton}
                    onClick={() => setSelectedDate('')}
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