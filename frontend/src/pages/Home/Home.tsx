import { FC, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Home.module.scss';
import { Header, Button, TaskStats } from '../../components';
import { useActivities } from '../../hooks/useActivities';
import { ROUTES } from '../../routes';

export interface HomeProps {}

export const Home: FC<HomeProps> = () => {
  const navigate = useNavigate();
  const { tasks, loading, fetchTasks } = useActivities();
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    inProgress: 0,
    withTimer: 0
  });

  useEffect(() => {
    // Загрузка всех задач для статистики
    fetchTasks();
  }, [fetchTasks]);

  useEffect(() => {
    // Подсчет статистики
    if (tasks.length > 0) {
      const completedTasks = tasks.filter(task => task.completed).length;
      const tasksWithTimer = tasks.filter(task => task.timerStatus === 'running' || task.timerStatus === 'paused').length;
      
      setStats({
        total: tasks.length,
        completed: completedTasks,
        inProgress: tasks.length - completedTasks,
        withTimer: tasksWithTimer
      });
    }
  }, [tasks]);

  const handleGoToTasks = () => {
    navigate(ROUTES.TASKS);
  };

  return (
    <div className={styles.pageWrapper}>
      <Header />
      <main className={styles.main}>
        <div className={styles.container}>
          <h1 className={styles.title}>План <span>Трекер</span></h1>
          <p className={styles.subtitle}>
            Удобный инструмент для управления задачами и отслеживания времени
          </p>

          {loading ? (
            <div className={styles.loading}>Загрузка данных...</div>
          ) : (
            <>
              {tasks.length > 0 ? (
                <div className={styles.statsSection}>
                  <TaskStats 
                    total={stats.total}
                    completed={stats.completed}
                    inProgress={stats.inProgress}
                    withTimer={stats.withTimer}
                  />
                </div>
              ) : (
                <div className={styles.emptyState}>
                  <div className={styles.emptyIcon}>📋</div>
                  <h2>У вас пока нет задач</h2>
                  <p>Создайте свою первую задачу, чтобы начать планировать время эффективно</p>
                </div>
              )}

              <div className={styles.actions}>
                <Button onClick={handleGoToTasks} variant="primary">
                  {tasks.length > 0 ? 'Перейти к задачам' : 'Создать задачу'}
                </Button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};