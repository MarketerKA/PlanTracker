import { FC, useEffect, useState, useCallback } from 'react';
import styles from './Timer.module.scss';
import { ConfirmDialog } from '../ConfirmDialog';

export interface TimerProps {
    isRunning: boolean;
    onStart: () => void;
    onPause: () => void;
    onStop: () => void;
    selectedTaskTitle: string | undefined;
    recordedTime?: number;
    lastTimerStart?: string; // UTC ISO string from server
}

export const Timer: FC<TimerProps> = ({ 
    isRunning, 
    onStart, 
    onPause, 
    onStop, 
    selectedTaskTitle,
    recordedTime = 0,
    lastTimerStart
}) => {
    // Calculate initial time including elapsed time if timer is running
    const calculateInitialTime = useCallback(() => {
        return recordedTime;
    }, [isRunning, lastTimerStart, recordedTime]); // eslint-disable-line

    const [time, setTime] = useState(calculateInitialTime());
    const [showStopConfirm, setShowStopConfirm] = useState(false);

    // Reset time when task changes or timer state changes
    useEffect(() => {
        setTime(calculateInitialTime());
    }, [calculateInitialTime]);

    // Update time when timer is running
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
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const handleStopClick = () => {
        setShowStopConfirm(true);
    };

    const handleStopConfirm = () => {
        onStop();
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
                    <button onClick={handleStopClick} disabled={!selectedTaskTitle}>Finish</button>
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
