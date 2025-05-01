import { FC } from 'react';
import styles from './TaskStats.module.scss';

export interface TaskStatsProps {
  total: number;
  completed: number;
  inProgress: number;
  withTimer: number;
}

export const TaskStats: FC<TaskStatsProps> = ({
  total,
  completed,
  inProgress,
  withTimer
}) => {
  // Вычисляем процент выполнения
  const completionPercentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  
  return (
    <div className={styles.statsWrapper}>
      <div className={styles.statsHeader}>
        <h2 className={styles.statsTitle}>Статистика задач</h2>
        <div className={styles.completionCircle}>
          <svg className={styles.progressCircle} width="60" height="60" viewBox="0 0 60 60">
            <circle 
              className={styles.progressBackground} 
              r="25" 
              cx="30" 
              cy="30" 
              fill="transparent" 
              strokeWidth="5"
            />
            <circle 
              className={styles.progressForeground} 
              r="25" 
              cx="30" 
              cy="30" 
              fill="transparent" 
              strokeWidth="5"
              strokeDasharray={`${2 * Math.PI * 25}`}
              strokeDashoffset={`${2 * Math.PI * 25 * (1 - completionPercentage / 100)}`}
            />
          </svg>
          <div className={styles.completionText}>{completionPercentage}%</div>
        </div>
      </div>
      
      <div className={styles.statsGrid}>
        <div className={styles.statItem}>
          <div className={styles.statValue}>{total}</div>
          <div className={styles.statLabel}>Всего задач</div>
        </div>
        
        <div className={styles.statItem}>
          <div className={styles.statValue}>{completed}</div>
          <div className={styles.statLabel}>Выполнено</div>
        </div>
        
        <div className={styles.statItem}>
          <div className={styles.statValue}>{inProgress}</div>
          <div className={styles.statLabel}>В процессе</div>
        </div>
        
        <div className={styles.statItem}>
          <div className={styles.statValue}>{withTimer}</div>
          <div className={styles.statLabel}>С таймером</div>
        </div>
      </div>
      
      <div className={styles.progressBars}>
        <div className={styles.progressItem}>
          <div className={styles.progressLabel}>
            <span>Выполнено</span>
            <span>{completionPercentage}%</span>
          </div>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill} 
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>
        
        <div className={styles.progressItem}>
          <div className={styles.progressLabel}>
            <span>В процессе</span>
            <span>{total > 0 ? Math.round((inProgress / total) * 100) : 0}%</span>
          </div>
          <div className={styles.progressBar}>
            <div 
              className={`${styles.progressFill} ${styles.inProgress}`}
              style={{ width: `${total > 0 ? (inProgress / total) * 100 : 0}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}; 