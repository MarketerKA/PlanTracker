import { FC, useMemo, useState } from 'react';
import Task, { TaskType } from '../Task';
import styles from './TaskList.module.scss';

interface TaskListProps {
  tasks: TaskType[];
  onToggleComplete: (id: string) => void;
  onDelete: (id: string) => void;
  itemsPerPage?: number;
}

const TaskList: FC<TaskListProps> = ({ 
  tasks, 
  onToggleComplete, 
  onDelete,
  itemsPerPage = 5
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  
  const totalPages = Math.ceil(tasks.length / itemsPerPage);
  
  const currentTasks = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return tasks.slice(startIndex, endIndex);
  }, [tasks, currentPage, itemsPerPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className={styles.taskList}>
      <div className={styles.list}>
        {currentTasks.length > 0 ? (
          currentTasks.map(task => (
            <Task
              key={task.id}
              task={task}
              onToggleComplete={onToggleComplete}
              onDelete={onDelete}
            />
          ))
        ) : (
          <div className={styles.emptyState}>Нет задач</div>
        )}
      </div>
      
      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button 
            className={styles.pageButton}
            disabled={currentPage === 1}
            onClick={() => handlePageChange(currentPage - 1)}
          >
            &laquo;
          </button>
          
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
            <button
              key={page}
              className={`${styles.pageButton} ${currentPage === page ? styles.active : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </button>
          ))}
          
          <button 
            className={styles.pageButton}
            disabled={currentPage === totalPages}
            onClick={() => handlePageChange(currentPage + 1)}
          >
            &raquo;
          </button>
        </div>
      )}
    </div>
  );
};

export default TaskList; 