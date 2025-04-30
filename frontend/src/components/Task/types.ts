export interface TaskType {
  id: string;
  title: string;
  completed: boolean;
  dueDate?: string;
  tags: string[];
}
