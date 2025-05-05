import { FC, useEffect, useState } from 'react';
import styles from './Timer.module.scss';
import { ConfirmDialog } from '../ConfirmDialog';

export interface TimerProps {
    isRunning: boolean;
    onStart: () => void;
    onPause: () => void;
    onStop: () => void;
    selectedTaskTitle: string | undefined;
}

export const Timer: FC<TimerProps> = ({ isRunning, onStart, onPause, onStop, selectedTaskTitle }) => {
    const [time, setTime] = useState(0);
    const [showStopConfirm, setShowStopConfirm] = useState(false);

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

    const handleStopClick = () => {
        setShowStopConfirm(true);
    };

    const handleStopConfirm = () => {
        onStop();
        setTime(0);
        setShowStopConfirm(false);
    };

    return (
        <>
            <div className={styles.timer}>
                <div className={styles.taskTitle}>
                    {selectedTaskTitle ? selectedTaskTitle : 'Select a task to track'}
                </div>
                <div className={styles.display}>{formatTime(time)}</div>
                <div className={styles.controls}>
                    <button onClick={onStart} disabled={isRunning || !selectedTaskTitle}>Start</button>
                    <button onClick={onPause} disabled={!isRunning}>Pause</button>
                    <button onClick={handleStopClick} disabled={!selectedTaskTitle}>Stop</button>
                </div>
            </div>

            <ConfirmDialog
                isOpen={showStopConfirm}
                title="Stop timer?"
                message="Are you sure you want to stop the timer? This action cannot be undone."
                confirmText="Stop"
                onConfirm={handleStopConfirm}
                onCancel={() => setShowStopConfirm(false)}
                variant="warning"
            />
        </>
    );
};
