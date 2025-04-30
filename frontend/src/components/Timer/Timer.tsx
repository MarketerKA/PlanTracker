import { FC, useEffect, useState } from 'react';
import styles from './Timer.module.scss';

export interface TimerProps {
    isRunning: boolean;
    onStart: () => void;
    onPause: () => void;
    onStop: () => void;
    selectedTaskTitle: string | undefined;
}

export const Timer: FC<TimerProps> = ({ isRunning, onStart, onPause, onStop, selectedTaskTitle }) => {
    const [time, setTime] = useState(0);

    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;

        if (isRunning) {
            interval = setInterval(() => {
                setTime(prev => prev + 1);
            }, 1000);
        }

        return () => clearInterval(interval);
    }, [isRunning]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className={styles.timer}>
            <div className={styles.taskTitle}>
                {selectedTaskTitle ? `${selectedTaskTitle}` : 'Выберите задачу для отслеживания'}
            </div>
            <div className={styles.display}>{formatTime(time)}</div>
            <div className={styles.controls}>
                <button onClick={onStart} disabled={isRunning}>Start</button>
                <button onClick={onPause} disabled={!isRunning}>Pause</button>
                <button onClick={() => {
                    onStop();
                    setTime(0);
                }}>Stop</button>
            </div>
        </div>
    );
};
