import { create } from 'zustand';
import type { GraphSnapshot, Paper, InnovationEdge } from '../api/types';

type LayoutMode = 'dagre' | 'cose';

interface GraphState {
  snapshot: GraphSnapshot | null;
  selectedNode: Paper | null;
  selectedEdge: InnovationEdge | null;
  layoutMode: LayoutMode;
  minConfidence: number;
  setSnapshot: (snapshot: GraphSnapshot) => void;
  selectNode: (paper: Paper | null) => void;
  selectEdge: (edge: InnovationEdge | null) => void;
  setLayoutMode: (mode: LayoutMode) => void;
  setMinConfidence: (val: number) => void;
  clear: () => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  snapshot: null,
  selectedNode: null,
  selectedEdge: null,
  layoutMode: 'cose',
  minConfidence: 0.5,
  setSnapshot: (snapshot) => set({ snapshot, selectedNode: null, selectedEdge: null }),
  selectNode: (paper) => set({ selectedNode: paper, selectedEdge: null }),
  selectEdge: (edge) => set({ selectedEdge: edge, selectedNode: null }),
  setLayoutMode: (mode) => set({ layoutMode: mode }),
  setMinConfidence: (val) => set({ minConfidence: val }),
  clear: () => set({ snapshot: null, selectedNode: null, selectedEdge: null }),
}));
