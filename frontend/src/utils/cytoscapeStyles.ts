import cytoscape from 'cytoscape';
import { RELATION_COLORS } from './edgeTaxonomy';

function hexToRgba(hex: string, alpha: number): string {
  const normalized = hex.replace('#', '');
  const value = Number.parseInt(normalized, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function nodeFill(ele: cytoscape.NodeSingular): string {
  if (ele.data('isSeed')) {
    return 'rgba(228, 188, 112, 0.97)';
  }

  const year = ele.data('year') || 2020;
  const size = ele.data('size') || 40;
  const degree = ele.data('degree') || 0;
  const yearShift = Math.max(0, Math.min(1, (year - 2012) / 14));
  const intensity = Math.max(0, Math.min(1, (size - 34) / 44));
  const prominence = Math.max(0, Math.min(1, degree / 4));
  const r = Math.round(190 - yearShift * 14 - prominence * 6);
  const g = Math.round(209 - intensity * 18 - prominence * 10);
  const b = Math.round(221 - yearShift * 12 + intensity * 4);
  const alpha = 0.54 + intensity * 0.18;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export const cytoscapeStyles: cytoscape.StylesheetStyle[] = [
  {
    selector: 'node',
    style: {
      'background-color': nodeFill,
      width: 'data(size)',
      height: 'data(size)',
      label: 'data(label)',
      'text-wrap': 'wrap',
      'text-max-width': (ele: cytoscape.NodeSingular) =>
        `${Math.max(50, Math.min(92, (ele.data('size') || 40) * 1.08))}px`,
      color: '#33464d',
      'font-family': '"Avenir Next", "Trebuchet MS", sans-serif',
      'font-weight': 700,
      'font-size': (ele: cytoscape.NodeSingular) =>
        Math.max(9, Math.min(15, (ele.data('size') || 40) * 0.16)),
      'text-valign': 'center',
      'text-halign': 'center',
      'text-margin-y': 0,
      'min-zoomed-font-size': 9,
      'text-outline-color': 'rgba(255, 255, 255, 0.92)',
      'text-outline-width': 2,
      'border-width': 1.2,
      'border-color': 'rgba(255, 255, 255, 0.96)',
      'overlay-opacity': 0,
      opacity: 1,
      'text-opacity': 0.9,
      'shadow-color': 'rgba(79, 101, 110, 0.14)',
      'shadow-blur': 22,
      'shadow-opacity': 0.7,
      'shadow-offset-y': 10,
      'transition-property': 'background-color, border-color, border-width, opacity, shadow-blur, shadow-opacity',
      'transition-duration': '220ms',
    } as Record<string, unknown>,
  },
  {
    selector: 'node[?isSeed]',
    style: {
      'border-width': 4,
      'border-color': '#8f57a9',
      'text-opacity': 1,
      label: 'data(emphasisLabel)',
      'font-size': 13,
      color: '#3b3020',
      'text-outline-color': 'rgba(255, 251, 240, 0.96)',
      'text-outline-width': 4,
      'text-valign': 'center',
      'text-margin-y': 0,
      'text-max-width': '88px',
      'shadow-color': 'rgba(143, 87, 169, 0.36)',
      'shadow-blur': 40,
      'shadow-offset-y': 18,
    },
  },
  {
    selector: 'node.context',
    style: {
      opacity: 0.98,
      'text-opacity': 0.92,
    },
  },
  {
    selector: 'node.focused',
    style: {
      label: 'data(emphasisLabel)',
      'border-width': 4,
      'border-color': '#945bb1',
      'shadow-color': 'rgba(148, 91, 177, 0.4)',
      'shadow-blur': 42,
      'shadow-offset-y': 20,
      opacity: 1,
    },
  },
  {
    selector: 'node.hovered',
    style: {
      label: 'data(emphasisLabel)',
      'text-opacity': 1,
      'shadow-blur': 34,
      'shadow-opacity': 1,
    },
  },
  {
    selector: 'node.faded',
    style: {
      opacity: 0.11,
      'text-opacity': 0.03,
      'shadow-opacity': 0,
    },
  },
  {
    selector: 'edge',
    style: {
      width: (ele: cytoscape.EdgeSingular) => 0.9 + ele.data('confidence') * 2.2,
      'line-color': (ele: cytoscape.EdgeSingular) =>
        hexToRgba(RELATION_COLORS[ele.data('relationType') as string] || '#7b8e95', 0.24),
      'target-arrow-shape': 'none',
      'curve-style': 'bezier',
      'line-cap': 'round',
      opacity: (ele: cytoscape.EdgeSingular) => 0.08 + ele.data('confidence') * 0.24,
      label: '',
      'font-size': '8px',
      'font-family': '"Avenir Next", "Trebuchet MS", sans-serif',
      color: '#4d6168',
      'text-background-color': 'rgba(255, 255, 255, 0.82)',
      'text-background-opacity': 1,
      'text-background-padding': '2px',
      'text-opacity': 0,
      'text-rotation': 'autorotate',
      'text-margin-y': -6,
      'overlay-opacity': 0,
      'transition-property': 'opacity, line-color, width, text-opacity',
      'transition-duration': '180ms',
    } as Record<string, unknown>,
  },
  {
    selector: 'edge.focus-edge, edge.hovered, edge:selected',
    style: {
      label: 'data(label)',
      width: (ele: cytoscape.EdgeSingular) => 2 + ele.data('confidence') * 3.2,
      'line-color': (ele: cytoscape.EdgeSingular) =>
        hexToRgba(RELATION_COLORS[ele.data('relationType') as string] || '#70848b', 0.72),
      opacity: 0.9,
      'text-opacity': 0.94,
    } as Record<string, unknown>,
  },
  {
    selector: 'edge.faded',
    style: {
      opacity: 0.04,
      'text-opacity': 0,
    },
  },
];
