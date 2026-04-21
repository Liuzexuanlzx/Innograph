import asyncio
import logging
from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel, Field

from app.agents.state import InnoGraphState
from app.models.edge import InnovationEdge, Verdict
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "verifier.txt"


class VerificationOutput(BaseModel):
    is_supported: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = ""


async def verifier(state: InnoGraphState) -> dict:
    """Verify candidate edges and assign confidence scores."""
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
            if result.confidence >= 0.5 and result.is_supported:
                edge.verdict = Verdict.SUPPORTED if result.confidence >= 0.7 else Verdict.WEAK
                return edge, True
            else:
                edge.verdict = Verdict.UNSUPPORTED
                return edge, False
        except Exception as e:
            logger.warning("Verification failed for edge %s->%s: %s",
                           edge.source_paper_id, edge.target_paper_id, e)
            return None, False

    # Process all candidates fully concurrently (DeepSeek has no strict rate limit)
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
