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
from app.models.paper import Paper
from app.services.cache import CacheService
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
    """Extract innovation relationships between paper pairs.

    Enforces temporal ordering: edges can only point from newer papers
    to older papers. This prevents nonsensical relationships like
    "2020 paper improves upon 2023 paper".
    """
    seed_id = state.get("seed_paper_id")
    paper_cards = state.get("paper_cards", [])
    raw_papers = state.get("raw_papers", [])

    if not seed_id or not paper_cards:
        return {"errors": ["Missing seed or paper cards for relation extraction"]}

    card_map = {c.paper_id: c for c in paper_cards}
    paper_map: dict[str, Paper] = {}
    year_map: dict[str, int] = {}
    for p in raw_papers:
        pid = p.openalex_id or p.s2_id or ""
        if pid:
            paper_map[pid] = p
            year_map[pid] = p.publication_year or 0

    def _get_ordered_pair(id_a: str, id_b: str) -> tuple[str, str]:
        a_year = year_map.get(id_a, 0) or 0
        b_year = year_map.get(id_b, 0) or 0
        if not a_year or not b_year:
            return (id_a, id_b)
        if a_year >= b_year:
            return (id_a, id_b)
        return (id_b, id_a)

    other_ids = [c.paper_id for c in paper_cards if c.paper_id != seed_id]
    seen_pairs: set[tuple[str, str]] = set()

    pairs: list[tuple[str, str]] = []
    for oid in other_ids:
        src, tgt = _get_ordered_pair(seed_id, oid)
        pair = (src, tgt)
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            pairs.append(pair)

    for i, id_a in enumerate(other_ids):
        for id_b in other_ids[i + 1:]:
            src, tgt = _get_ordered_pair(id_a, id_b)
            pair = (src, tgt)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                pairs.append(pair)

    logger.info("Generating %d temporally-ordered pairs (reduced from %d bidirectional)",
                 len(pairs), len(other_ids) * 2)

    llm = LLMProvider()
    cache = CacheService()
    template = Template(PROMPT_PATH.read_text())
    edges = []

    async def _extract_one(src_id: str, tgt_id: str) -> InnovationEdge | None:
        cached = await cache.get_edge(src_id, tgt_id)
        if cached:
            logger.debug("Using cached edge %s->%s", src_id, tgt_id)
            return InnovationEdge(**cached)

        src_card = card_map.get(src_id)
        tgt_card = card_map.get(tgt_id)
        if not src_card or not tgt_card:
            return None

        src_paper = paper_map.get(src_id)
        tgt_paper = paper_map.get(tgt_id)

        src_year = year_map.get(src_id, 0) or 0
        tgt_year = year_map.get(tgt_id, 0) or 0

        prompt = template.render(
            source_title=f"{src_paper.title if src_paper else src_id} ({src_year})",
            source_card=src_card.model_dump(),
            target_title=f"{tgt_paper.title if tgt_paper else tgt_id} ({tgt_year})",
            target_card=tgt_card.model_dump(),
        )
        try:
            result = await llm.complete(
                [{"role": "user", "content": prompt}],
                response_model=RelationOutput,
            )
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

            edge = InnovationEdge(
                source_paper_id=src_id,
                target_paper_id=tgt_id,
                relation_type=rel_type,
                innovation_dimensions=dims,
                operations=ops,
                summary=result.summary,
                evidence=evidence,
            )
            await cache.set_edge(src_id, tgt_id, edge.model_dump())
            return edge
        except Exception as e:
            logger.warning("Relation extraction failed for %s->%s: %s", src_id, tgt_id, e)
            return None

    results = await asyncio.gather(*[_extract_one(s, t) for s, t in pairs])
    edges = [e for e in results if e is not None]

    logger.info("Extracted %d candidate edges", len(edges))

    paper_pairs = [(e.source_paper_id, e.target_paper_id) for e in edges]

    return {"candidate_edges": edges, "paper_pairs": paper_pairs}
