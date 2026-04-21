import type { RelationType } from '../../api/types';
import { RELATION_COLORS, RELATION_LABELS } from '../../utils/edgeTaxonomy';

interface Props {
  type: RelationType;
}

export function EdgeTypeBadge({ type }: Props) {
  const color = RELATION_COLORS[type] || '#94a3b8';

  return (
    <span
      className="rounded-full px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-white shadow-sm"
      style={{ backgroundColor: color }}
    >
      {RELATION_LABELS[type] || type}
    </span>
  );
}
