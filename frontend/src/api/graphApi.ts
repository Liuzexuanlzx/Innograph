import client from './client';
import type { GraphSnapshot, TaskResult, Paper } from './types';

export async function buildGraph(params: {
  query: string;
  depth?: number;
  max_papers?: number;
  min_confidence?: number;
}): Promise<{ task_id: string }> {
  const { data } = await client.post('/graph/build', params);
  return data;
}

export async function getTaskStatus(taskId: string): Promise<TaskResult> {
  const { data } = await client.get(`/graph/tasks/${taskId}`);
  return data;
}

export async function getTaskSnapshot(taskId: string): Promise<GraphSnapshot> {
  const { data } = await client.get(`/graph/tasks/${taskId}/snapshot`);
  return data;
}

export async function searchPapers(query: string): Promise<Paper[]> {
  const { data } = await client.get('/papers/search', { params: { q: query } });
  return data;
}
