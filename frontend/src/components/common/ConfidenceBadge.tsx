interface Props {
  confidence: number;
}

export function ConfidenceBadge({ confidence }: Props) {
  const pct = Math.round(confidence * 100);
  let color = 'bg-red-100 text-red-700';
  if (confidence >= 0.7) color = 'bg-green-100 text-green-700';
  else if (confidence >= 0.5) color = 'bg-yellow-100 text-yellow-700';

  return (
    <span className={`rounded-full px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] ${color}`}>
      {pct}%
    </span>
  );
}
