export interface Paper {
  openalex_id: string | null;
  doi: string | null;
  s2_id: string | null;
  title: string;
  abstract: string | null;
  authors: string[];
  publication_year: number | null;
  venue: string | null;
  citation_count: number;
  reference_count: number;
  fields_of_study: string[];
  url: string | null;
}

export interface PaperCard {
  paper_id: string;
  short_label: string;
  problem: string;
  method_summary: string;
  key_modules: string[];
  claimed_gains: string[];
  limitations: string[];
  datasets: string[];
  baselines: string[];
}

export type RelationType =
  | 'IMPROVES_ON' | 'EXTENDS' | 'COMBINES_WITH' | 'APPLIES_TO'
  | 'SIMPLIFIES' | 'GENERALIZES' | 'PROVIDES_THEORY_FOR'
  | 'REPRODUCES' | 'CONTRADICTS';

export type InnovationDimension =
  | 'ACCURACY' | 'EFFICIENCY' | 'SCALABILITY' | 'ROBUSTNESS'
  | 'GENERALIZATION' | 'INTERPRETABILITY' | 'DATA_EFFICIENCY'
  | 'SIMPLICITY' | 'NOVELTY' | 'COVERAGE' | 'FAIRNESS'
  | 'SAFETY' | 'COST' | 'USABILITY';

export type Operation =
  | 'ADDS_MODULE' | 'REPLACES_BACKBONE' | 'CHANGES_LOSS_FUNCTION'
  | 'MODIFIES_ARCHITECTURE' | 'INTRODUCES_PRETRAINING'
  | 'ADDS_DATA_AUGMENTATION' | 'CHANGES_OPTIMIZATION'
  | 'ADDS_REGULARIZATION' | 'INTRODUCES_NEW_TASK'
  | 'CHANGES_REPRESENTATION' | 'SCALES_UP' | 'ADDS_FEEDBACK_LOOP'
  | 'INTRODUCES_BENCHMARK' | 'PROVIDES_PROOF' | 'COMBINES_MODALITIES';

export type Verdict = 'SUPPORTED' | 'WEAK' | 'UNSUPPORTED';

export interface EvidenceSpan {
  paper_id: string;
  text: string;
  section: string | null;
  score: number;
}

export interface InnovationEdge {
  id: string | null;
  source_paper_id: string;
  target_paper_id: string;
  relation_type: RelationType;
  innovation_dimensions: InnovationDimension[];
  operations: Operation[];
  confidence: number;
  verdict: Verdict;
  evidence: EvidenceSpan[];
  summary: string;
}

export interface GraphSnapshot {
  papers: Paper[];
  paper_cards: PaperCard[];
  innovation_edges: InnovationEdge[];
  summaries: Record<string, unknown>;
  seed_paper_id: string | null;
}

export type TaskStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED';

export interface TaskResult {
  task_id: string;
  status: TaskStatus;
  progress: string;
  error: string | null;
}
