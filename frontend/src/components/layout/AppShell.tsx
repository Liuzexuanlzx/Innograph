import { useEffect, useState, type CSSProperties } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { GraphCanvas } from '../graph/GraphCanvas';
import { useGraphStore } from '../../stores/graphStore';
import { useGraphBuild } from '../../hooks/useGraphBuild';

const EXAMPLES = [
  {
    label: 'ReAct',
    query: 'https://arxiv.org/abs/2210.03629',
  },
  {
    label: 'Transformers',
    query: 'Attention Is All You Need',
  },
  {
    label: 'Swin',
    query: 'Swin Transformer',
  },
];

export function AppShell() {
  const snapshot = useGraphStore((s) => s.snapshot);
  const { startBuild } = useGraphBuild();
  const [headerElement, setHeaderElement] = useState<HTMLElement | null>(null);
  const [headerOffset, setHeaderOffset] = useState(148);

  useEffect(() => {
    if (!headerElement) return;

    const updateOffset = () => {
      const height = Math.ceil(headerElement.getBoundingClientRect().height);
      setHeaderOffset(height + 10);
    };

    updateOffset();

    const observer = new ResizeObserver(() => updateOffset());
    observer.observe(headerElement);

    return () => observer.disconnect();
  }, [headerElement]);

  const shellStyle = {
    '--hud-offset': `${headerOffset}px`,
  } as CSSProperties;

  return (
    <div className="app-shell relative h-screen overflow-hidden" style={shellStyle}>
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[8%] top-[8%] h-64 w-64 rounded-full bg-amber-200/30 blur-3xl" />
        <div className="absolute right-[10%] top-[12%] h-72 w-72 rounded-full bg-teal-200/40 blur-3xl" />
        <div className="absolute bottom-[8%] left-[18%] h-72 w-72 rounded-full bg-violet-200/20 blur-3xl" />
      </div>

      <Header headerRef={setHeaderElement} />

      <main className="relative h-full px-3 pb-3 pt-[var(--hud-offset)] md:px-6 md:pb-6">
        <section className="graph-stage h-full overflow-hidden rounded-[34px] border border-white/70">
          {snapshot ? (
            <GraphCanvas />
          ) : (
            <div className="flex h-full items-center justify-center px-6">
              <div className="max-w-4xl text-center">
                <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                  Dynamic Literature Landscape
                </p>
                <h2 className="mt-5 text-4xl font-semibold leading-tight text-slate-900 md:text-6xl">
                  Explore research lineages as a living map.
                </h2>
                <p className="mx-auto mt-6 max-w-2xl text-base leading-8 text-slate-600 md:text-lg">
                  Start from a single paper, then trace adjacent methods, theoretical ancestors, and
                  practical descendants in an interactive graph inspired by connected-paper style exploration.
                </p>

                <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
                  {EXAMPLES.map((example) => (
                    <button
                      key={example.label}
                      onClick={() => startBuild(example.query)}
                      className="rounded-full bg-white/82 px-5 py-3 text-sm font-semibold text-slate-700 shadow-[0_16px_40px_rgba(60,82,87,0.1)] transition hover:-translate-y-0.5 hover:bg-white"
                    >
                      {example.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        {snapshot && <Sidebar />}
      </main>
    </div>
  );
}
