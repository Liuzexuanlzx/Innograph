import type { Ref } from 'react';
import { SearchBar } from '../search/SearchBar';
import { useTaskStore } from '../../stores/taskStore';

interface HeaderProps {
  headerRef?: Ref<HTMLElement>;
}

export function Header({ headerRef }: HeaderProps) {
  const { status, progress, error } = useTaskStore();

  return (
    <header ref={headerRef} className="pointer-events-none absolute inset-x-0 top-0 z-30 p-3 md:px-6 md:pb-0 md:pt-2">
      <div className="pointer-events-auto mx-auto flex max-w-[1600px] flex-col gap-2.5 md:flex-row md:items-stretch md:gap-3">
        <div className="glass-panel flex flex-col rounded-[28px] px-5 py-4 md:h-[108px] md:w-[250px] md:justify-center md:py-2.5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-500">
            Research Cartography
          </p>
          <h1 className="mt-1 text-3xl font-semibold text-slate-900">InnoGraph</h1>
          <p className="mt-1 text-[13px] leading-5 text-slate-600">
            Trace how ideas branch, converge, and reappear across papers.
          </p>
        </div>

        <div className="glass-panel flex flex-1 flex-col justify-center rounded-[28px] px-4 py-2.5 md:h-[108px] md:px-5 md:py-2">
          <SearchBar />
        </div>

        <div className="glass-panel flex flex-col rounded-[28px] px-4 py-3 md:h-[108px] md:w-[238px] md:justify-center md:py-2.5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
            Build Status
          </p>

          {!status && (
            <p className="mt-1 text-[13px] leading-5 text-slate-600">
              Ready to map a paper into a dynamic innovation graph.
            </p>
          )}

          {status && status !== 'SUCCESS' && status !== 'FAILED' && (
            <div className="mt-2.5 flex items-start gap-3">
              <span className="mt-0.5 inline-block h-3.5 w-3.5 rounded-full border-2 border-slate-900 border-t-transparent animate-spin" />
              <div>
                <p className="text-sm font-semibold text-slate-900">
                  {status === 'PENDING' ? 'Queued' : 'Building'}
                </p>
                <p className="mt-1 text-sm leading-relaxed text-slate-600">{progress || status}</p>
              </div>
            </div>
          )}

          {status === 'SUCCESS' && (
            <p className="mt-1 text-[13px] font-semibold leading-5 text-emerald-700">
              Graph ready. Explore the cluster.
            </p>
          )}

          {status === 'FAILED' && (
            <p className="mt-1 text-[13px] leading-5 text-rose-600">{error || 'Build failed.'}</p>
          )}
        </div>
      </div>
    </header>
  );
}
