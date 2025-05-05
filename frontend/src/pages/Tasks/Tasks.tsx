import { FC, useState } from 'react';
import styles from './Tasks.module.scss';
import { Header, Todo, TaskStats } from '../../components';
import { useActivities } from '../../hooks/useActivities';

// Using Record<string, never> instead of empty interface
type TasksProps = Record<string, never>;

export const Tasks: FC<TasksProps> = () => {
  const { tasks, loading } = useActivities();
  const [activeTab, setActiveTab] = useState<'all' | 'stats'>('all');

  // Calculate statistics for TaskStats
  const stats = {
    total: tasks.length,
    completed: tasks.filter(task => task.completed).length,
    inProgress: tasks.filter(task => !task.completed).length,
    withTimer: tasks.filter(task => task.timerStatus === 'running' || task.timerStatus === 'paused').length
  };

  return (
    <div className={styles.pageWrapper}>
      <Header />
      <main className={styles.main}>
        <div className={styles.container}>
          <div className={styles.tasksHeader}>
            <h1 className={styles.title}>My Tasks</h1>
            
            <div className={styles.tabsContainer}>
              <button 
                className={`${styles.tabButton} ${activeTab === 'all' ? styles.active : ''}`} 
                onClick={() => setActiveTab('all')}
              >
                Tasks
              </button>
              <button 
                className={`${styles.tabButton} ${activeTab === 'stats' ? styles.active : ''}`} 
                onClick={() => setActiveTab('stats')}
              >
                Statistics
              </button>
            </div>
          </div>
          
          {activeTab === 'all' ? (
            <Todo />
          ) : (
            <div className={styles.statsContainer}>
              {loading ? (
                <div className={styles.loading}>Loading data...</div>
              ) : (
                <TaskStats
                  total={stats.total}
                  completed={stats.completed}
                  inProgress={stats.inProgress}
                  withTimer={stats.withTimer}
                />
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}; 