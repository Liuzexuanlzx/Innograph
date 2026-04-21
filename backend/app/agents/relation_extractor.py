import asyncio
import logging
from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel, Field

from app.agents.state import InnoGraphState
from app.models.edge import (
    InnovationEdge, RelationType, InnovationDimension,
    Operation, EvidenceSpan,
)
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "relation_extractor.txt"


class RelationOutput(BaseModel):
    relation_type: str
    innovation_dimensions: list[str] = Field(default_factory=list)
    operations: list[str] = Field(default_factory=list)
    summary: str = ""
    evidence_text_source: str = ""
    evidence_text_target: str = ""


async def relation_extractor(state: InnoGraphState) -> dict:
    """Extract innovation relationships between paper pairs."""
    seed_id = state.get("seed_paper_id")
    paper_cards = state.get("paper_cards", [])
    raw_papers = state.get("raw_papers", [])

    if not seed_id or not paper_cards:
        return {"errors": ["Missing seed or paper cards for relation extraction"]}

    # Build lookup
    card_map = {c.paper_id: c for c in paper_cards}
    paper_map = {
        (p.openalex_id or p.s2_id or ""): p
        for p in raw_papers
    }

    # Generate pairs: (seed, each_other) and (each_other, seed)
    other_ids = [c.paper_id for c in paper_cards if c.paper_id != seed_id]
    pairs = [(seed_id, oid) for oid in other_ids] + [(oid, seed_id) for oid in other_ids]

    llm = LLMProvider()
    template = Template(PROMPT_PATH.read_text())
    edges = []

    async def _extract_one(src_id: str, tgt_id: str) -> InnovationEdge | None:
        src_card = card_map.get(src_id)
        tgt_card = card_map.get(tgt_id)
        if not src_card or not tgt_card:
            return None

        src_paper = paper_map.get(src_id)
        tgt_paper = paper_map.get(tgt_id)

        prompt = template.render(
            source_title=src_paper.title if src_paper else src_id,
            source_card=src_card.model_dump(),
            target_title=tgt_paper.title if tgt_paper else tgt_id,
            target_card=tgt_card.model_dump(),
        )
        try:
            result = await llm.complete(
                [{"role": "user", "content": prompt}],
                response_model=RelationOutput,
            )
            # Parse enum values safely
            try:
                rel_type = RelationType(result.relation_type)
            except ValueError:
                rel_type = RelationType.EXTENDS

            dims = []
            for d in result.innovation_dimensions:
                try:
                    dims.append(InnovationDimension(d))
                except ValueError:
                    pass

            ops = []
            for o in result.operations:
                try:
                    ops.append(Operation(o))
                except ValueError:
                    pass

            evidence = []
            if result.evidence_text_source:
                evidence.append(EvidenceSpan(paper_id=src_id, text=result.evidence_text_source))
            if result.evidence_text_target:
                evidence.append(EvidenceSpan(paper_id=tgt_id, text=result.evidence_text_target))

            return InnovationEdge(
                source_paper_id=src_id,
                target_paper_id=tgt_id,
                relation_type=rel_type,
                innovation_dimensions=dims,
                operations=ops,
                summary=result.summary,
                evidence=evidence,
            )
        except Exception as e:
            logger.warning("Relation extraction failed for %s->%s: %s", src_id, tgt_id, e)
            return None

    # Process all pairs fully concurrently (DeepSeek has no strict rate limit)
    results = await asyncio.gather(*[_extract_one(s, t) for s, t in pairs])
    edges = [e for e in results if e is not None]

    logger.info("Extracted %d candidate edges", len(edges))

    # Generate paper_pairs for state
    paper_pairs = [(e.source_paper_id, e.target_paper_id) for e in edges]

    return {"candidate_edges": edges, "paper_pairs": paper_pairs}
