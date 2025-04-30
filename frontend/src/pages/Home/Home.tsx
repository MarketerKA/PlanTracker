import { FC, useState, useEffect } from 'react';
import styles from './Home.module.scss';
import { Header, TaskForm, TaskList, TaskType } from '../../components';
import { v4 as uuidv4 } from 'uuid';

// Демо-задачи для тестирования
const demoTasks: TaskType[] = [
  {
    id: uuidv4(),
    title: 'Изучить React',
    completed: true,
    priority: 'high',
    dueDate: '2023-10-01'
  },
  {
    id: uuidv4(),
    title: 'Разработать компоненты',
    completed: false,
    priority: 'medium',
    dueDate: '2023-10-10'
  },
  {
    id: uuidv4(),
    title: 'Добавить стили',
    completed: false,
    priority: 'low',
    dueDate: '2023-10-15'
  },
  {
    id: uuidv4(),
    title: 'Создать систему маршрутизации',
    completed: false,
    priority: 'medium'
  },
  {
    id: uuidv4(),
    title: 'Интегрировать API',
    completed: false,
    priority: 'high',
    dueDate: '2023-11-01'
  },
  {
    id: uuidv4(),
    title: 'Написать тесты',
    completed: false,
    priority: 'low',
    dueDate: '2023-11-15'
  },
  {
    id: uuidv4(),
    title: 'Оптимизировать производительность',
    completed: false,
    priority: 'medium'
  },
  {
    id: uuidv4(),
    title: 'Проверить кроссбраузерность',
    completed: false,
    priority: 'low'
  }
];

export interface HomeProps {}

export const Home: FC<HomeProps> = () => {
  const [tasks, setTasks] = useState<TaskType[]>([]);

  // Загрузка задач из localStorage при инициализации
  useEffect(() => {
    const savedTasks = localStorage.getItem('tasks');
    if (savedTasks) {
      try {
        setTasks(JSON.parse(savedTasks));
      } catch (e) {
        console.error('Ошибка при загрузке задач:', e);
        // Если произошла ошибка, загружаем демо-задачи
        setTasks(demoTasks);
      }
    } else {
      // Если задач в localStorage нет, загружаем демо-задачи
      setTasks(demoTasks);
    }
  }, []);

  // Сохранение задач в localStorage при изменении
  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const handleAddTask = (task: Omit<TaskType, 'id'>) => {
    const newTask: TaskType = {
      ...task,
      id: uuidv4(),
    };
    setTasks(prev => [newTask, ...prev]);
  };

  const handleToggleComplete = (id: string) => {
    setTasks(prev => 
      prev.map(task => 
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const handleDeleteTask = (id: string) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  return (
    <div className={styles.pageWrapper}>
      <Header />
      <main className={styles.main}>
        <div className={styles.container}>
          <h1 className={styles.title}>Мои задачи</h1>
          
          <div className={styles.content}>
            <TaskForm onAddTask={handleAddTask} />
            <TaskList 
              tasks={tasks} 
              onToggleComplete={handleToggleComplete} 
              onDelete={handleDeleteTask}
              itemsPerPage={5}
            />
          </div>
        </div>
      </main>
    </div>
  );
}; 