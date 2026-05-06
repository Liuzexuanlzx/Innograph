import { useCallback, useRef } from 'react';
import { buildGraph, getTaskStatus, getTaskSnapshot } from '../api/graphApi';
import { useTaskStore } from '../stores/taskStore';
import { useGraphStore } from '../stores/graphStore';

function getErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null) {
    const candidate = error as {
      message?: string;
      response?: { data?: { detail?: string; error?: string } };
    };

    const backendError = candidate.response?.data?.error;
    if (typeof backendError === 'string' && backendError) {
      return backendError;
    }

    const detail = candidate.response?.data?.detail;
    if (typeof detail === 'string' && detail) {
      return detail;
    }

    if (typeof candidate.message === 'string' && candidate.message) {
      return candidate.message;
    }
  }

  return 'Unknown error';
}

export function useGraphBuild() {
  const { setTask, updateStatus } = useTaskStore();
  const { setSnapshot } = useGraphStore();
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const inFlightRef = useRef(false);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    inFlightRef.current = false;
  }, []);

  const startBuild = useCallback(async (query: string) => {
    stopPolling();
    try {
      const { task_id } = await buildGraph({ query, max_papers: 40, depth: 2 });
      setTask(task_id);

      pollingRef.current = setInterval(async () => {
        if (inFlightRef.current) {
          return;
        }
        inFlightRef.current = true;
        try {
          const status = await getTaskStatus(task_id);
          updateStatus(status);

          if (status === 'SUCCESS') {
            stopPolling();
            const snapshot = await getTaskSnapshot(task_id);
            setSnapshot(snapshot);
          } else if (status === 'FAILURE') {
            stopPolling();
          }
        } catch {
        } finally {
          inFlightRef.current = false;
        }
      }, 2000);
    } catch (error) {
      alert(getErrorMessage(error));
    }
  }, [stopPolling, setTask, updateStatus, setSnapshot]);

  return { startBuild, stopPolling };
}
