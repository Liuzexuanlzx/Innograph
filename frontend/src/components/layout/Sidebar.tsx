import { useEffect, useState, type PointerEvent as ReactPointerEvent } from 'react';
import { useGraphStore } from '../../stores/graphStore';
import { PaperDetailPanel } from '../panels/PaperDetailPanel';
import { EdgeDetailPanel } from '../panels/EdgeDetailPanel';
import { SummaryPanel } from '../panels/SummaryPanel';
import { GraphControls } from '../graph/GraphControls';

type SidebarTab = 'overview' | 'inspect' | 'controls';

const TAB_LABELS: Record<SidebarTab, string> = {
  overview: 'Overview',
  inspect: 'Inspect',
  controls: 'Controls',
};

const DEFAULT_DETAIL_WIDTH = 640;
const MIN_DETAIL_WIDTH = 440;
const MAX_DETAIL_WIDTH = 920;
const DETAIL_WIDTH_STORAGE_KEY = 'innograph.detailPanelWidth';

export function Sidebar() {
  const { selectedNode, selectedEdge, snapshot } = useGraphStore();
  const [activeTab, setActiveTab] = useState<SidebarTab>('overview');
  const [detailWidth, setDetailWidth] = useState(DEFAULT_DETAIL_WIDTH);
  const [isResizing, setIsResizing] = useState(false);

  useEffect(() => {
    if (selectedNode || selectedEdge) {
      setActiveTab('inspect');
    }
  }, [selectedEdge, selectedNode]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const savedWidth = window.localStorage.getItem(DETAIL_WIDTH_STORAGE_KEY);
    if (!savedWidth) return;

    const parsedWidth = Number.parseInt(savedWidth, 10);
    if (!Number.isNaN(parsedWidth)) {
      setDetailWidth(Math.max(MIN_DETAIL_WIDTH, Math.min(MAX_DETAIL_WIDTH, parsedWidth)));
    }
  }, []);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    document.body.classList.toggle('is-resizing-panel', isResizing);
    return () => document.body.classList.remove('is-resizing-panel');
  }, [isResizing]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const clampWidthToViewport = () => {
      const responsiveMaxWidth = Math.min(MAX_DETAIL_WIDTH, Math.max(MIN_DETAIL_WIDTH, window.innerWidth - 360));
      setDetailWidth((currentWidth) => Math.min(currentWidth, responsiveMaxWidth));
    };

    clampWidthToViewport();
    window.addEventListener('resize', clampWidthToViewport);
    return () => window.removeEventListener('resize', clampWidthToViewport);
  }, []);

  const inspectTitle = selectedNode
    ? 'Selected paper'
    : selectedEdge
      ? 'Selected relation'
      : 'No selection';
  const activeLabel =
    activeTab === 'overview'
      ? 'Narrative'
      : activeTab === 'inspect'
        ? 'Detail'
        : 'Layout and Filters';
  const activeTitle =
    activeTab === 'overview'
      ? 'Innovation Storyline'
      : activeTab === 'inspect'
        ? inspectTitle
        : 'Graph Settings';
  const activeDescription =
    activeTab === 'overview'
      ? 'Read the main arc, the seed innovation, and the major branches.'
      : activeTab === 'inspect'
        ? 'Inspect one paper or relation in depth.'
        : 'Tune the layout and confidence threshold for the current map.';
  const visibleLinks = snapshot?.innovation_edges.length || 0;
  const selectedFocus = selectedNode?.title || selectedEdge?.summary || inspectTitle;
  const detailPanelWidth = Math.max(MIN_DETAIL_WIDTH, Math.min(MAX_DETAIL_WIDTH, detailWidth));

  const startResize = (clientX: number) => {
    if (typeof window === 'undefined') return;

    const startX = clientX;
    const startWidth = detailPanelWidth;
    const viewportWidth = window.innerWidth;
    const responsiveMaxWidth = Math.min(MAX_DETAIL_WIDTH, Math.max(MIN_DETAIL_WIDTH, viewportWidth - 360));
    let lastWidth = startWidth;

    const onPointerMove = (event: PointerEvent) => {
      const deltaX = event.clientX - startX;
      const nextWidth = Math.max(
        MIN_DETAIL_WIDTH,
        Math.min(responsiveMaxWidth, Math.round(startWidth - deltaX)),
      );
      lastWidth = nextWidth;
      setDetailWidth(nextWidth);
    };

    const stopResize = () => {
      setIsResizing(false);
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', stopResize);
      window.removeEventListener('pointercancel', stopResize);
      window.localStorage.setItem(DETAIL_WIDTH_STORAGE_KEY, String(lastWidth));
    };

    setIsResizing(true);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', stopResize);
    window.addEventListener('pointercancel', stopResize);
  };

  const handleResizePointerDown = (event: ReactPointerEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    startResize(event.clientX);
  };

  const resetDetailWidth = () => {
    setDetailWidth(DEFAULT_DETAIL_WIDTH);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(DETAIL_WIDTH_STORAGE_KEY, String(DEFAULT_DETAIL_WIDTH));
    }
  };

  const renderPanelContent = () => (
    <>
      {activeTab === 'overview' && snapshot?.summaries && <SummaryPanel summaries={snapshot.summaries} />}
      {activeTab === 'overview' && !snapshot?.summaries && (
        <div className="p-5 text-sm text-slate-500">No summaries available yet.</div>
      )}

      {activeTab === 'inspect' && selectedNode && <PaperDetailPanel paper={selectedNode} />}
      {activeTab === 'inspect' && selectedEdge && <EdgeDetailPanel edge={selectedEdge} />}
      {activeTab === 'inspect' && !selectedNode && !selectedEdge && (
        <div className="p-5 text-sm leading-7 text-slate-500">
          Click a node or edge in the graph to inspect it here.
        </div>
      )}

      {activeTab === 'controls' && <GraphControls />}
    </>
  );

  return (
    <>
      <aside className="pointer-events-none absolute inset-x-3 bottom-3 z-20 md:hidden">
        <div className="pointer-events-auto flex h-[44vh] max-h-[44vh] min-h-[360px] flex-col gap-3">
          <div className="glass-panel rounded-[30px] px-5 py-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Explorer
                </p>
                <h3 className="mt-2 text-2xl font-semibold text-slate-900">Graph Studio</h3>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  Read the map, inspect one thread, or tune the graph view.
                </p>
              </div>
              <div className="rounded-2xl bg-slate-900 px-3 py-2 text-right text-white shadow-lg shadow-slate-900/15">
                <div className="text-[10px] uppercase tracking-[0.22em] text-white/65">Seed</div>
                <div className="mt-1 text-xs font-semibold">{snapshot?.seed_paper_id || 'Unknown'}</div>
              </div>
            </div>

            {snapshot && (
              <div className="mt-4 grid grid-cols-3 gap-2">
                <div className="rounded-2xl bg-white/72 px-3 py-3">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Papers</div>
                  <div className="mt-2 text-lg font-semibold text-slate-900">{snapshot.papers.length}</div>
                </div>
                <div className="rounded-2xl bg-white/72 px-3 py-3">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Links</div>
                  <div className="mt-2 text-lg font-semibold text-slate-900">{visibleLinks}</div>
                </div>
                <div className="rounded-2xl bg-white/72 px-3 py-3">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Focus</div>
                  <div className="mt-2 text-sm font-semibold text-slate-900">{inspectTitle}</div>
                </div>
              </div>
            )}

            <div className="mt-4 grid grid-cols-3 gap-2">
              {(Object.keys(TAB_LABELS) as SidebarTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`rounded-2xl px-3 py-3 text-sm font-semibold transition ${
                    activeTab === tab
                      ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/15'
                      : 'bg-white/74 text-slate-600 hover:bg-white'
                  }`}
                >
                  {TAB_LABELS[tab]}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-panel flex min-h-0 flex-1 flex-col overflow-hidden rounded-[30px]">
            <div className="border-b border-slate-200/70 px-5 py-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                {activeLabel}
              </p>
              <h3 className="mt-2 text-2xl font-semibold text-slate-900">{activeTitle}</h3>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto">{renderPanelContent()}</div>
          </div>
        </div>
      </aside>

      <div className="pointer-events-none absolute inset-0 z-20 hidden md:block">
        <aside className="absolute left-6 top-[calc(var(--hud-offset)+0.5rem)] w-[min(24vw,340px)] xl:w-[320px]">
          <div className="pointer-events-auto glass-panel flex flex-col rounded-[30px] px-5 py-3.5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Explorer
                </p>
                <h3 className="mt-1.5 text-2xl font-semibold text-slate-900">Graph Studio</h3>
                <p className="mt-1 text-[13px] leading-5 text-slate-600">
                  Map overview and quick view controls.
                </p>
              </div>
              <div className="rounded-2xl bg-slate-900 px-3 py-2 text-right text-white shadow-lg shadow-slate-900/15">
                <div className="text-[10px] uppercase tracking-[0.22em] text-white/65">Seed</div>
                <div className="mt-1 text-xs font-semibold">{snapshot?.seed_paper_id || 'Unknown'}</div>
              </div>
            </div>

            {snapshot && (
              <div className="mt-3 grid grid-cols-3 gap-2">
                <div className="rounded-2xl bg-white/72 px-3 py-2.5">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Papers</div>
                  <div className="mt-1.5 text-base font-semibold text-slate-900">{snapshot.papers.length}</div>
                </div>
                <div className="rounded-2xl bg-white/72 px-3 py-2.5">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Links</div>
                  <div className="mt-1.5 text-base font-semibold text-slate-900">{visibleLinks}</div>
                </div>
                <div className="rounded-2xl bg-white/72 px-3 py-2.5">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Focus</div>
                  <div className="mt-1.5 truncate text-[13px] font-semibold leading-5 text-slate-900">
                    {selectedFocus}
                  </div>
                </div>
              </div>
            )}

            <div className="mt-3 grid grid-cols-3 gap-2">
              {(Object.keys(TAB_LABELS) as SidebarTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`rounded-2xl px-3 py-2.5 text-center text-xs font-semibold transition ${
                    activeTab === tab
                      ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/15'
                      : 'bg-white/74 text-slate-600 hover:bg-white'
                  }`}
                >
                  {TAB_LABELS[tab]}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <aside
          className="absolute bottom-6 right-6 top-[calc(var(--hud-offset)+0.5rem)]"
          style={{ width: `${detailPanelWidth}px` }}
        >
          <button
            type="button"
            aria-label="Resize detail panel"
            title="Drag to resize. Double click to reset width."
            onPointerDown={handleResizePointerDown}
            onDoubleClick={resetDetailWidth}
            className="pointer-events-auto absolute -left-3 top-8 z-10 hidden h-[calc(100%-4rem)] w-6 cursor-col-resize rounded-full md:flex md:items-center md:justify-center"
          >
            <span
              className={`h-20 w-1 rounded-full transition ${
                isResizing ? 'bg-slate-900/60 shadow-[0_0_0_8px_rgba(15,23,42,0.08)]' : 'bg-slate-500/18 hover:bg-slate-500/30'
              }`}
            />
          </button>

          <div className="pointer-events-auto glass-panel flex h-full min-h-0 flex-col overflow-hidden rounded-[30px]">
            <div className="border-b border-slate-200/70 px-5 py-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                    {activeLabel}
                  </p>
                  <h3 className="mt-2 text-2xl font-semibold text-slate-900">{activeTitle}</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{activeDescription}</p>
                </div>
                <button
                  type="button"
                  onClick={resetDetailWidth}
                  className="rounded-full bg-white/70 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500 transition hover:bg-white"
                >
                  Reset
                </button>
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto">{renderPanelContent()}</div>
          </div>
        </aside>
      </div>
    </>
  );
}
