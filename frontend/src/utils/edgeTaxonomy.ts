import type { RelationType, InnovationDimension } from '../api/types';

export const RELATION_COLORS: Record<string, string> = {
  IMPROVES_ON: '#3b82f6',
  EXTENDS: '#22c55e',
  COMBINES_WITH: '#a855f7',
  APPLIES_TO: '#f97316',
  SIMPLIFIES: '#06b6d4',
  GENERALIZES: '#6366f1',
  PROVIDES_THEORY_FOR: '#ec4899',
  REPRODUCES: '#78716c',
  CONTRADICTS: '#ef4444',
};

export const RELATION_LABELS: Record<RelationType, string> = {
  IMPROVES_ON: 'Improves On',
  EXTENDS: 'Extends',
  COMBINES_WITH: 'Combines With',
  APPLIES_TO: 'Applies To',
  SIMPLIFIES: 'Simplifies',
  GENERALIZES: 'Generalizes',
  PROVIDES_THEORY_FOR: 'Provides Theory For',
  REPRODUCES: 'Reproduces',
  CONTRADICTS: 'Contradicts',
};

export const DIMENSION_LABELS: Record<InnovationDimension, string> = {
  ACCURACY: 'Accuracy',
  EFFICIENCY: 'Efficiency',
  SCALABILITY: 'Scalability',
  ROBUSTNESS: 'Robustness',
  GENERALIZATION: 'Generalization',
  INTERPRETABILITY: 'Interpretability',
  DATA_EFFICIENCY: 'Data Efficiency',
  SIMPLICITY: 'Simplicity',
  NOVELTY: 'Novelty',
  COVERAGE: 'Coverage',
  FAIRNESS: 'Fairness',
  SAFETY: 'Safety',
  COST: 'Cost',
  USABILITY: 'Usability',
};
