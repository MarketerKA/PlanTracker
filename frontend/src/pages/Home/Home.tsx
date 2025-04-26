import { FC } from 'react';
import styles from './Home.module.scss';
import Button from '../../components/Button';

const Home: FC = () => {
  return (
    <div className={styles.home}>
      <h1>Домашняя страница</h1>
      <p>Добро пожаловать в приложение!</p>
      <div className={styles.buttons}>
        <Button>Первичная кнопка</Button>
        <Button variant="secondary">Вторичная кнопка</Button>
      </div>
    </div>
  );
};

export default Home; 