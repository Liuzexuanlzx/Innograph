import { useGraphStore } from '../../stores/graphStore';

export function GraphControls() {
  const { layoutMode, setLayoutMode, minConfidence, setMinConfidence, snapshot } = useGraphStore();

  if (!snapshot) return null;

  const visibleEdges = snapshot.innovation_edges.filter((edge) => edge.confidence >= minConfidence).length;

  return (
    <div className="px-5 py-5">
      <div className="rounded-[24px] bg-white/72 px-4 py-4">
        <p className="text-sm text-slate-600">
          {snapshot.papers.length} papers and {visibleEdges} visible links are currently in frame.
        </p>
      </div>

      <div className="mt-5 space-y-5">
        <div>
          <label className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
            Layout
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setLayoutMode('cose')}
              className={`rounded-2xl px-4 py-3 text-left text-sm transition ${
                layoutMode === 'cose'
                  ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/15'
                  : 'bg-white/80 text-slate-700 hover:bg-white'
              }`}
            >
              <div className="font-semibold">Clusters</div>
              <div className={`mt-1 text-xs ${layoutMode === 'cose' ? 'text-white/70' : 'text-slate-500'}`}>
                Force-directed, more like Connected Papers
              </div>
            </button>
            <button
              onClick={() => setLayoutMode('dagre')}
              className={`rounded-2xl px-4 py-3 text-left text-sm transition ${
                layoutMode === 'dagre'
                  ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/15'
                  : 'bg-white/80 text-slate-700 hover:bg-white'
              }`}
            >
              <div className="font-semibold">Lineage</div>
              <div className={`mt-1 text-xs ${layoutMode === 'dagre' ? 'text-white/70' : 'text-slate-500'}`}>
                Vertical flow for explicit ancestor-descendant reading
              </div>
            </button>
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              Confidence
            </label>
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
              {minConfidence.toFixed(1)}+
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={minConfidence}
            onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
            className="w-full accent-slate-900"
          />
          <p className="mt-2 text-xs text-slate-500">
            Raise this to filter weaker inferred innovation links.
          </p>
        </div>

        <div className="rounded-[24px] bg-slate-900 px-4 py-4 text-white shadow-[0_18px_46px_rgba(15,23,42,0.16)]">
          <div className="text-[10px] uppercase tracking-[0.22em] text-white/55">Seed Paper</div>
          <div className="mt-2 text-sm font-semibold">{snapshot.seed_paper_id || 'Unknown'}</div>
        </div>
      </div>
    </div>
  );
}
