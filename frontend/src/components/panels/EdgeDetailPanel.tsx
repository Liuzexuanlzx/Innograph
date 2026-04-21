import type { InnovationEdge } from '../../api/types';
import { EdgeTypeBadge } from '../common/EdgeTypeBadge';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { DIMENSION_LABELS, RELATION_LABELS } from '../../utils/edgeTaxonomy';
import { useGraphStore } from '../../stores/graphStore';
import { paperMatchesId } from '../../utils/paperIds';

interface Props {
  edge: InnovationEdge;
}

export function EdgeDetailPanel({ edge }: Props) {
  const snapshot = useGraphStore((state) => state.snapshot);
  const sourcePaper = snapshot?.papers.find((paper) => paperMatchesId(paper, edge.source_paper_id));
  const targetPaper = snapshot?.papers.find((paper) => paperMatchesId(paper, edge.target_paper_id));

  return (
    <div className="space-y-5 px-5 py-5">
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
          Selected Relation
        </p>
        <h3 className="mt-2 text-2xl font-semibold text-slate-900">
          {RELATION_LABELS[edge.relation_type] || edge.relation_type}
        </h3>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <EdgeTypeBadge type={edge.relation_type} />
        <ConfidenceBadge confidence={edge.confidence} />
        <span className="rounded-full bg-slate-900/6 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-slate-600">
          {edge.verdict.toLowerCase()}
        </span>
      </div>

      <div className="rounded-[26px] bg-white/70 px-4 py-4">
        <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Direction</p>
        <div className="mt-3 space-y-3 text-sm leading-6 text-slate-700">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Source</div>
            <div className="mt-1 font-semibold text-slate-900">
              {sourcePaper?.title || edge.source_paper_id}
            </div>
          </div>
          <div className="text-slate-400">↓</div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Target</div>
            <div className="mt-1 font-semibold text-slate-900">
              {targetPaper?.title || edge.target_paper_id}
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-[26px] bg-slate-900 px-4 py-4 text-white shadow-[0_18px_46px_rgba(15,23,42,0.16)]">
        <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">Summary</p>
        <p className="mt-3 text-sm leading-7 text-white/90">{edge.summary || 'No summary available.'}</p>
      </div>

      {edge.innovation_dimensions.length > 0 && (
        <div>
          <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Innovation Dimensions
          </h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {edge.innovation_dimensions.map((dimension) => (
              <span
                key={dimension}
                className="rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-semibold text-emerald-700"
              >
                {DIMENSION_LABELS[dimension] || dimension}
              </span>
            ))}
          </div>
        </div>
      )}

      {edge.operations.length > 0 && (
        <div>
          <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Operations
          </h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {edge.operations.map((operation) => (
              <span
                key={operation}
                className="rounded-full bg-violet-100 px-3 py-1.5 text-xs font-semibold text-violet-700"
              >
                {operation.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {edge.evidence.length > 0 && (
        <div>
          <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Evidence</h4>
          <div className="mt-3 space-y-3">
            {edge.evidence.map((evidence, index) => (
              <div key={`${evidence.paper_id}-${index}`} className="rounded-[24px] bg-white/70 px-4 py-4">
                <p className="text-sm italic leading-7 text-slate-700">“{evidence.text}”</p>
                <p className="mt-2 text-xs text-slate-500">
                  From {snapshot?.papers.find((paper) => paperMatchesId(paper, evidence.paper_id))?.title || evidence.paper_id}
                  {evidence.section ? ` · ${evidence.section}` : ''}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
