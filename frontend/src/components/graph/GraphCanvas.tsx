import { useCallback, useState } from 'react';
import { useGraphStore } from '../../stores/graphStore';
import { useCytoscape } from '../../hooks/useCytoscape';
import type { Paper, InnovationEdge } from '../../api/types';
import { NodeTooltip } from './NodeTooltip';

export function GraphCanvas() {
  const [containerElement, setContainerElement] = useState<HTMLDivElement | null>(null);
  const {
    snapshot,
    layoutMode,
    minConfidence,
    selectedNode,
    selectedEdge,
    selectNode,
    selectEdge,
  } = useGraphStore();
  const [hoveredNode, setHoveredNode] = useState<{
    paper: Paper;
    position: { x: number; y: number };
  } | null>(null);

  const onNodeClick = useCallback((paper: Paper) => selectNode(paper), [selectNode]);
  const onEdgeClick = useCallback((edge: InnovationEdge) => selectEdge(edge), [selectEdge]);
  const onCanvasClick = useCallback(() => {
    selectNode(null);
    selectEdge(null);
  }, [selectNode, selectEdge]);
  const onNodeHover = useCallback((paper: Paper, position: { x: number; y: number }) => {
    setHoveredNode({ paper, position });
  }, []);
  const onNodeLeave = useCallback(() => setHoveredNode(null), []);

  useCytoscape({
    container: containerElement,
    snapshot,
    layout: layoutMode,
    minConfidence,
    onNodeClick,
    onEdgeClick,
    onCanvasClick,
    onNodeHover,
    onNodeLeave,
  });

  const visibleEdges = snapshot?.innovation_edges.filter((edge) => edge.confidence >= minConfidence).length || 0;
  const focusLabel = selectedNode?.title || selectedEdge?.summary || null;

  return (
    <div className="relative h-full w-full overflow-hidden">
      <div
        ref={setContainerElement}
        className="graph-canvas absolute inset-0"
        style={{ minHeight: '400px' }}
      />

      <div className="pointer-events-none absolute inset-x-4 top-3 z-10 flex flex-wrap items-start gap-2.5 md:hidden">
        <div className="glass-panel rounded-full px-3.5 py-1.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
          Dynamic innovation map
        </div>
        {snapshot && (
          <>
            <div className="glass-panel rounded-full px-3.5 py-1.5 text-[13px] text-slate-700">
              {snapshot.papers.length} papers
            </div>
            <div className="glass-panel rounded-full px-3.5 py-1.5 text-[13px] text-slate-700">
              {visibleEdges} visible links
            </div>
          </>
        )}
      </div>

      <div className="pointer-events-none absolute bottom-4 left-4 z-10 flex max-w-md flex-col gap-2">
        <div className="glass-panel rounded-2xl px-4 py-3 text-sm text-slate-600">
          Drag nodes to reshape clusters. Scroll to zoom. Click a paper to isolate its neighborhood.
        </div>
        {focusLabel && (
          <div className="glass-panel rounded-2xl px-4 py-3">
            <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Focus</p>
            <p className="mt-1 text-sm font-semibold text-slate-800">{focusLabel}</p>
          </div>
        )}
      </div>

      {hoveredNode && <NodeTooltip paper={hoveredNode.paper} position={hoveredNode.position} />}
    </div>
  );
}
