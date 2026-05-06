import asyncio
import logging
import re
from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel, Field

from app.agents.state import InnoGraphState
from app.models.edge import InnovationEdge, Verdict
from app.models.paper import PaperCard
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "verifier.txt"

_TITLE_TOKENS_RE = re.compile(r"[a-zA-Z]+")

MIN_CARD_INFO_TOKENS = 20
MIN_CARD_SCORE = 3
PRE_SCREEN_OVERLAP_THRESHOLD = 0.03
MIN_EVIDENCE_LENGTH = 10


class VerificationOutput(BaseModel):
    is_supported: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = ""


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TITLE_TOKENS_RE.findall(text) if len(t) > 2}


def _collect_card_tokens(card: PaperCard) -> set[str]:
    tokens = set()
    for field in [card.problem, card.method_summary, card.short_label]:
        tokens |= _tokenize(field)
    for lst in [card.key_modules, card.claimed_gains, card.datasets, card.baselines]:
        for item in lst:
            tokens |= _tokenize(item)
    return {t for t in tokens if len(t) > 3}


def _card_quality_score(card: PaperCard) -> int:
    score = 0
    if card.problem and len(card.problem) > 10:
        score += 1
    if card.method_summary and len(card.method_summary) > 20:
        score += 1
    if card.short_label:
        score += 1
    if card.key_modules:
        score += 1
    if card.claimed_gains:
        score += 1
    return score


def _evidence_in_card(evidence_text: str, card_texts: list[str]) -> bool:
    if not evidence_text or len(evidence_text) < MIN_EVIDENCE_LENGTH:
        return False
    evidence_lower = evidence_text.lower()
    for text in card_texts:
        if evidence_lower in text.lower():
            return True
    return False


def _check_domain_mismatch(card_a: PaperCard, card_b: PaperCard) -> bool:
    a_tokens = _collect_card_tokens(card_a)
    b_tokens = _collect_card_tokens(card_b)
    if not a_tokens or not b_tokens:
        return False
    overlap = len(a_tokens & b_tokens)
    return overlap == 0


def _keyword_overlap(card_a: PaperCard, card_b: PaperCard) -> float:
    a = _collect_card_tokens(card_a)
    b = _collect_card_tokens(card_b)
    if not a or not b:
        return 0.0
    intersection = a & b
    return len(intersection) / max(len(min(a, b, key=len)), 1)


async def verifier(state: InnoGraphState) -> dict:
    """Verify candidate edges with strict anti-hallucination checks.

    Three-stage pipeline:
    1. Rule-based pre-screening (keyword overlap, domain mismatch, sparse cards)
    2. Evidence cross-validation (verify evidence text actually appears in cards)
    3. LLM verification for remaining candidates
    """
    candidates = state.get("candidate_edges", [])
    if not candidates:
        return {"errors": ["No candidate edges to verify"]}

    paper_cards = state.get("paper_cards", [])
    card_map = {c.paper_id: c for c in paper_cards}

    llm = LLMProvider()
    template = Template(PROMPT_PATH.read_text())

    verified = []
    rejected = []

    async def _verify_one(edge: InnovationEdge) -> tuple[InnovationEdge | None, bool]:
        src_card = card_map.get(edge.source_paper_id)
        tgt_card = card_map.get(edge.target_paper_id)

        if src_card and tgt_card:
            overlap = _keyword_overlap(src_card, tgt_card)
            if overlap < PRE_SCREEN_OVERLAP_THRESHOLD:
                edge.confidence = 0.1
                edge.verdict = Verdict.UNSUPPORTED
                logger.debug(
                    "Rejected %s->%s (overlap=%.3f < %.3f)",
                    edge.source_paper_id, edge.target_paper_id,
                    overlap, PRE_SCREEN_OVERLAP_THRESHOLD,
                )
                return edge, False

            if _check_domain_mismatch(src_card, tgt_card):
                edge.confidence = 0.1
                edge.verdict = Verdict.UNSUPPORTED
                logger.debug(
                    "Rejected %s->%s (domain mismatch)",
                    edge.source_paper_id, edge.target_paper_id,
                )
                return edge, False

            src_score = _card_quality_score(src_card)
            tgt_score = _card_quality_score(tgt_card)
            if src_score < MIN_CARD_SCORE or tgt_score < MIN_CARD_SCORE:
                edge.confidence = 0.15
                edge.verdict = Verdict.UNSUPPORTED
                logger.debug(
                    "Rejected %s->%s (sparse cards: src=%d tgt=%d < %d)",
                    edge.source_paper_id, edge.target_paper_id,
                    src_score, tgt_score, MIN_CARD_SCORE,
                )
                return edge, False

        src_texts = []
        tgt_texts = []
        if src_card:
            src_texts = [src_card.problem, src_card.method_summary,
                         src_card.short_label] + src_card.key_modules
        if tgt_card:
            tgt_texts = [tgt_card.problem, tgt_card.method_summary,
                         tgt_card.short_label] + tgt_card.key_modules

        evidence_ok = True
        for ev in edge.evidence:
            if ev.paper_id == edge.source_paper_id:
                if not _evidence_in_card(ev.text, src_texts):
                    evidence_ok = False
                    break
            elif ev.paper_id == edge.target_paper_id:
                if not _evidence_in_card(ev.text, tgt_texts):
                    evidence_ok = False
                    break

        if not evidence_ok:
            edge.confidence = 0.2
            edge.verdict = Verdict.UNSUPPORTED
            logger.debug(
                "Rejected %s->%s (evidence text not found in cards)",
                edge.source_paper_id, edge.target_paper_id,
            )
            return edge, False

        prompt = template.render(
            source_id=edge.source_paper_id,
            target_id=edge.target_paper_id,
            source_card=src_card.model_dump() if src_card else {},
            target_card=tgt_card.model_dump() if tgt_card else {},
            relation_type=edge.relation_type.value,
            summary=edge.summary,
            evidence=[e.model_dump() for e in edge.evidence],
        )
        try:
            result = await llm.complete(
                [{"role": "user", "content": prompt}],
                response_model=VerificationOutput,
            )
            edge.confidence = result.confidence
            if result.confidence >= 0.7 and result.is_supported:
                edge.verdict = Verdict.SUPPORTED if result.confidence >= 0.85 else Verdict.WEAK
                return edge, True
            else:
                edge.verdict = Verdict.UNSUPPORTED
                return edge, False
        except Exception as e:
            logger.warning("Verification failed for edge %s->%s: %s",
                           edge.source_paper_id, edge.target_paper_id, e)
            return None, False

    results = await asyncio.gather(*[_verify_one(e) for e in candidates])
    for edge, is_verified in results:
        if edge is None:
            continue
        if is_verified:
            verified.append(edge)
        else:
            rejected.append((edge.source_paper_id, edge.target_paper_id))

    logger.info("Verified: %d, Rejected: %d", len(verified), len(rejected))

    iteration = state.get("iteration", 0) + 1
    return {
        "verified_edges": verified,
        "rejected_pairs": rejected,
        "iteration": iteration,
    }
