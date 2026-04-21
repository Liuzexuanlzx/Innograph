import { useState, type FormEvent } from 'react';
import { useGraphBuild } from '../../hooks/useGraphBuild';
import { useTaskStore } from '../../stores/taskStore';

export function SearchBar() {
  const [query, setQuery] = useState('');
  const { startBuild } = useGraphBuild();
  const { status } = useTaskStore();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    startBuild(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="h-full w-full">
      <div className="flex h-full flex-col gap-1.5 md:justify-center">
        <div className="flex items-center gap-2 rounded-[22px] border border-white/70 bg-white/85 px-4 py-2 shadow-[0_18px_45px_rgba(63,84,92,0.12)] backdrop-blur-xl md:py-1.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-900 text-white shadow-lg shadow-slate-900/15">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.7">
              <path d="M11 4a7 7 0 1 0 4.91 11.99L20 20" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Paste an arXiv URL, DOI, or paper title"
            className="min-w-0 flex-1 bg-transparent text-sm text-slate-800 outline-none placeholder:text-slate-400"
            aria-label="Search for a paper"
          />

          <button
            type="submit"
            className="rounded-2xl bg-slate-900 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-slate-800 md:py-1.5"
          >
            {status === 'RUNNING' || status === 'PENDING' ? 'Mapping…' : 'Map Graph'}
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1.5 pl-1 text-[11px] text-slate-500 md:hidden">
          <span className="font-semibold uppercase tracking-[0.18em] text-slate-400">Try</span>
          <button
            type="button"
            onClick={() => {
              const sample = 'https://arxiv.org/abs/2210.03629';
              setQuery(sample);
              startBuild(sample);
            }}
            className="rounded-full bg-white/70 px-3 py-1 text-slate-600 transition hover:bg-white"
          >
            ReAct
          </button>
          <button
            type="button"
            onClick={() => {
              const sample = 'Attention Is All You Need';
              setQuery(sample);
              startBuild(sample);
            }}
            className="rounded-full bg-white/70 px-3 py-1 text-slate-600 transition hover:bg-white"
          >
            Attention Is All You Need
          </button>
        </div>
      </div>
    </form>
  );
}
