import type { Paper } from '../../api/types';
import { useGraphStore } from '../../stores/graphStore';
import { getPaperId } from '../../utils/paperIds';

interface Props {
  paper: Paper;
}

export function PaperDetailPanel({ paper }: Props) {
  const snapshot = useGraphStore((s) => s.snapshot);
  const card = snapshot?.paper_cards.find((candidate) => candidate.paper_id === getPaperId(paper));

  return (
    <div className="space-y-5 px-5 py-5">
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
          Selected Paper
        </p>
        <h3 className="mt-2 text-2xl font-semibold leading-tight text-slate-900">{paper.title}</h3>
        {card?.short_label && (
          <div className="mt-3 inline-flex rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-white">
            {card.short_label}
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="rounded-2xl bg-white/70 px-3 py-3">
          <div className="text-[10px] uppercase tracking-[0.22em] text-slate-400">Year</div>
          <div className="mt-2 text-sm font-semibold text-slate-800">{paper.publication_year || '—'}</div>
        </div>
        <div className="rounded-2xl bg-white/70 px-3 py-3">
          <div className="text-[10px] uppercase tracking-[0.22em] text-slate-400">Citations</div>
          <div className="mt-2 text-sm font-semibold text-slate-800">
            {paper.citation_count.toLocaleString()}
          </div>
        </div>
        <div className="rounded-2xl bg-white/70 px-3 py-3">
          <div className="text-[10px] uppercase tracking-[0.22em] text-slate-400">Refs</div>
          <div className="mt-2 text-sm font-semibold text-slate-800">{paper.reference_count}</div>
        </div>
      </div>

      <div className="space-y-2 text-sm leading-7 text-slate-600">
        <p>{paper.authors.slice(0, 6).join(', ')}{paper.authors.length > 6 ? ' et al.' : ''}</p>
        <p>
          {paper.venue || 'Unknown venue'}
          {paper.publication_year ? ` · ${paper.publication_year}` : ''}
        </p>
        {paper.doi && (
          <a
            href={`https://doi.org/${paper.doi}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-white"
          >
            DOI
          </a>
        )}
      </div>

      {paper.abstract && (
        <div className="rounded-[24px] bg-white/70 px-4 py-4">
          <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">Abstract</p>
          <p className="mt-3 text-sm leading-7 text-slate-700">{paper.abstract}</p>
        </div>
      )}

      {paper.fields_of_study.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Fields
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {paper.fields_of_study.map((field) => (
              <span
                key={field}
                className="rounded-full bg-slate-900/6 px-3 py-1.5 text-xs font-semibold text-slate-700"
              >
                {field}
              </span>
            ))}
          </div>
        </div>
      )}

      {card && (
        <div className="space-y-4 rounded-[28px] bg-slate-900 px-4 py-4 text-white shadow-[0_18px_46px_rgba(15,23,42,0.16)]">
          {card.problem && (
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">Problem</h4>
              <p className="mt-2 text-sm leading-7 text-white/90">{card.problem}</p>
            </div>
          )}

          {card.method_summary && (
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">Method</h4>
              <p className="mt-2 text-sm leading-7 text-white/90">{card.method_summary}</p>
            </div>
          )}

          {card.key_modules.length > 0 && (
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">
                Key Modules
              </h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {card.key_modules.map((module, index) => (
                  <span
                    key={`${module}-${index}`}
                    className="rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-white/85"
                  >
                    {module}
                  </span>
                ))}
              </div>
            </div>
          )}

          {card.claimed_gains.length > 0 && (
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">
                Claimed Gains
              </h4>
              <ul className="mt-3 space-y-2 text-sm leading-7 text-white/85">
                {card.claimed_gains.map((gain, index) => (
                  <li key={`${gain}-${index}`}>• {gain}</li>
                ))}
              </ul>
            </div>
          )}

          {card.limitations.length > 0 && (
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">
                Limitations
              </h4>
              <ul className="mt-3 space-y-2 text-sm leading-7 text-white/85">
                {card.limitations.map((limitation, index) => (
                  <li key={`${limitation}-${index}`}>• {limitation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
