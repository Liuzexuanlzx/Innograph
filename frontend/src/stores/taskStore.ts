import { create } from 'zustand';
import type { TaskStatus } from '../api/types';

interface TaskState {
  taskId: string | null;
  status: TaskStatus | null;
  progress: string;
  error: string | null;
  setTask: (taskId: string) => void;
  updateStatus: (status: TaskStatus, progress?: string, error?: string | null) => void;
  clear: () => void;
}

export const useTaskStore = create<TaskState>((set) => ({
  taskId: null,
  status: null,
  progress: '',
  error: null,
  setTask: (taskId) => set({ taskId, status: 'PENDING', progress: '', error: null }),
  updateStatus: (status, progress = '', error = null) => set({ status, progress, error }),
  clear: () => set({ taskId: null, status: null, progress: '', error: null }),
}));
