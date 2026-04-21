import type { Paper } from '../api/types';

export function getPaperId(paper: Paper): string {
  return paper.openalex_id || paper.s2_id || paper.doi || paper.title;
}

export function paperMatchesId(paper: Paper, id: string): boolean {
  return getPaperId(paper) === id;
}
