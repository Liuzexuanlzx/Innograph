interface Props {
  summaries: Record<string, unknown>;
}

export function SummaryPanel({ summaries }: Props) {
  const lineage = summaries.lineage_summary as string | undefined;
  const branches = summaries.branch_summaries as string[] | undefined;
  const seedSummary = summaries.seed_innovation_summary as string | undefined;

  if (!lineage && !branches?.length && !seedSummary) {
    return (
      <div className="px-5 py-5 text-sm text-slate-500">
        No summaries available yet.
      </div>
    );
  }

  return (
    <div className="space-y-5 px-5 py-5">
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
          Narrative Overview
        </p>
        <h3 className="mt-2 text-2xl font-semibold text-slate-900">Innovation Storyline</h3>
      </div>

      {seedSummary && (
        <section className="rounded-[28px] bg-slate-900 px-4 py-4 text-white shadow-[0_18px_46px_rgba(15,23,42,0.16)]">
          <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/55">
            Seed Paper Innovation
          </h4>
          <p className="mt-3 text-sm leading-7 text-white/90">{seedSummary}</p>
        </section>
      )}

      {lineage && (
        <section className="rounded-[28px] bg-white/70 px-4 py-4">
          <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Innovation Lineage
          </h4>
          <p className="mt-3 text-sm leading-7 text-slate-700">{lineage}</p>
        </section>
      )}

      {branches && branches.length > 0 && (
        <section>
          <h4 className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Innovation Branches
          </h4>
          <div className="mt-3 space-y-3">
            {branches.map((branch, index) => (
              <div
                key={`${branch}-${index}`}
                className="rounded-[24px] border border-white/70 bg-white/72 px-4 py-4 shadow-[0_10px_26px_rgba(60,82,87,0.08)]"
              >
                <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-400">
                  Branch {index + 1}
                </div>
                <p className="mt-2 text-sm leading-7 text-slate-700">{branch}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
