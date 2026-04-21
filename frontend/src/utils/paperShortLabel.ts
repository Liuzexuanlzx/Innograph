import type { Paper, PaperCard } from '../api/types';

const STOPWORDS = new Set([
  'a',
  'an',
  'and',
  'are',
  'as',
  'at',
  'by',
  'for',
  'from',
  'in',
  'into',
  'is',
  'of',
  'on',
  'or',
  'the',
  'to',
  'towards',
  'with',
]);

function cleanShortLabel(label: string): string {
  const cleaned = label.replace(/\s+/g, ' ').trim().replace(/^[\s\-:;,]+|[\s\-:;,]+$/g, '');
  return cleaned.length > 24 ? `${cleaned.slice(0, 24).trim()}…` : cleaned;
}

export function inferShortLabelFromTitle(title: string): string {
  const cleanTitle = title.replace(/\s+/g, ' ').trim();
  if (!cleanTitle) return '';

  const [prefix] = cleanTitle.split(':');
  if (prefix && prefix !== cleanTitle && prefix.length <= 24 && prefix.split(/\s+/).length <= 4) {
    return cleanShortLabel(prefix);
  }

  const parenMatch = cleanTitle.match(/\(([A-Za-z][A-Za-z0-9-]{1,18})\)/);
  if (parenMatch) {
    return cleanShortLabel(parenMatch[1]);
  }

  const tokens = cleanTitle.replace(/\//g, ' ').split(/\s+/);
  const acronymTokens: string[] = [];
  for (const token of tokens) {
    const stripped = token.replace(/^[,.;:()[\]{}]+|[,.;:()[\]{}]+$/g, '');
    if (!stripped) continue;
    if (/^[A-Z]{2,10}$/.test(stripped)) return cleanShortLabel(stripped);
    if (/[A-Z]/.test(stripped.slice(1)) && stripped.length <= 18) return cleanShortLabel(stripped);
    if (/^[A-Z]/.test(stripped) && !STOPWORDS.has(stripped.toLowerCase())) {
      acronymTokens.push(stripped[0].toUpperCase());
    }
  }

  const acronym = acronymTokens.slice(0, 6).join('');
  if (acronym.length >= 2 && acronym.length <= 8) return acronym;

  const keywords = tokens
    .map((token) => token.replace(/^[,.;:()[\]{}]+|[,.;:()[\]{}]+$/g, ''))
    .filter((token) => token && !STOPWORDS.has(token.toLowerCase()));
  return cleanShortLabel(keywords.slice(0, 2).join(' '));
}

export function resolvePaperShortLabel(paper: Paper, card?: PaperCard | null): string {
  const candidate = cleanShortLabel(card?.short_label || '');
  if (candidate) return candidate;
  return inferShortLabelFromTitle(paper.title);
}
