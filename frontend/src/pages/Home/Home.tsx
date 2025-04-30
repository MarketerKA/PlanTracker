import { FC } from 'react';
import styles from './Home.module.scss';
import Header from '../../components/Header';
import Button from '../../components/Button';

const Home: FC = () => {
  return (
    <div className={styles.pageWrapper}>
      <Header />
      <main className={styles.main}>
        <section className={styles.hero}>
          <div className={styles.container}>
            <div className={styles.heroContent}>
              <h1>Управляйте временем <span>эффективно</span></h1>
              <p>
                Простая система планирования задач и отслеживания времени
                для повышения продуктивности
              </p>
              <div className={styles.cta}>
                <Button>Начать</Button>
              </div>
            </div>
            <div className={styles.heroImage}>
              <div className={styles.mockup}>
                <div className={styles.mockupHeader}></div>
                <div className={styles.mockupContent}>
                  <div className={styles.mockupItem}></div>
                  <div className={styles.mockupItem}></div>
                  <div className={styles.mockupItem}></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.features}>
          <div className={styles.container}>
            <h2>Возможности</h2>
            <div className={styles.featureGrid}>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>◷</div>
                <h3>Учет времени</h3>
                <p>Автоматическое и ручное отслеживание времени задач</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>☑</div>
                <h3>Задачи</h3>
                <p>Простое управление задачами с приоритизацией</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>📊</div>
                <h3>Аналитика</h3>
                <p>Визуализация продуктивности и затраченного времени</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Home; 