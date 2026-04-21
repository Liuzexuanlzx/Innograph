import type { Paper } from '../../api/types';

interface Props {
  paper: Paper;
  position: { x: number; y: number };
}

export function NodeTooltip({ paper, position }: Props) {
  return (
    <div
      className="pointer-events-none absolute z-30 max-w-sm rounded-3xl border border-white/70 bg-white/88 px-4 py-3 shadow-[0_24px_60px_rgba(60,82,87,0.18)] backdrop-blur-xl"
      style={{ left: position.x + 14, top: position.y + 14 }}
    >
      <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Paper</p>
      <h4 className="mt-1 text-sm font-semibold leading-tight text-slate-900">{paper.title}</h4>
      <p className="mt-2 text-xs text-slate-600">
        {paper.authors.slice(0, 3).join(', ')}
        {paper.authors.length > 3 && ' et al.'}
      </p>
      <p className="mt-2 text-xs text-slate-500">
        {paper.venue || 'Unknown venue'}
        {paper.publication_year ? ` · ${paper.publication_year}` : ''}
        {` · ${paper.citation_count.toLocaleString()} citations`}
      </p>
    </div>
  );
}
