import asyncio
import logging

from app.agents.state import InnoGraphState
from app.services.openalex import OpenAlexClient
from app.services.semantic_scholar import SemanticScholarClient

logger = logging.getLogger(__name__)

_SOURCE_LIMIT = 80


async def retrieval(state: InnoGraphState) -> dict:
    """Fetch references, citations, and recommendations for the seed paper.

    Strategy:
    - Always query BOTH OpenAlex and Semantic Scholar concurrently.
    - Collect up to _SOURCE_LIMIT papers per source per direction.
    - Deduplicate by title, then rank by citation_count (desc).
    - Keep the top max_papers most-cited papers for downstream analysis.
    """
    seed_id = state.get("seed_paper_id")
    if not seed_id:
        return {"errors": ["No seed paper ID available"]}

    plan = state.get("retrieval_plan", {})
    max_papers = plan.get("max_papers", 40)
    existing_papers = state.get("raw_papers", [])
    seed_paper = existing_papers[0] if existing_papers else None

    oa = OpenAlexClient()
    s2 = SemanticScholarClient()

    seen_titles: set[str] = {
        (p.title or "").lower().strip()
        for p in existing_papers
        if (p.title or "").strip()
    }
    papers: list = []

    def _add(paper_list):
        for p in paper_list:
            key = (p.title or "").lower().strip()
            if key and key not in seen_titles:
                seen_titles.add(key)
                papers.append(p)

    async def _fetch(label: str, coro, empty_value):
        try:
            result = await coro
            if isinstance(result, list):
                logger.info("Retrieved %d papers from %s", len(result), label)
            else:
                logger.info("Retrieved result from %s: %s", label, "found" if result else "empty")
            return result
        except Exception as e:
            logger.warning("Retrieval error from %s (non-fatal): %s", label, e)
            return empty_value

    try:
        oa_refs_coro   = _fetch("OpenAlex references",    oa.get_references(seed_id, limit=_SOURCE_LIMIT),   [])
        oa_cites_coro  = _fetch("OpenAlex citations",     oa.get_citations(seed_id, limit=_SOURCE_LIMIT),    [])
        oa_related_coro = _fetch("OpenAlex related works", oa.get_related_works(seed_id),                       [])
        s2_match_coro  = _fetch("Semantic Scholar match", s2.match_paper(seed_paper.title), None) if seed_paper else asyncio.sleep(0, result=None)

        oa_refs, oa_cites, oa_related, s2_match = await asyncio.gather(
            oa_refs_coro, oa_cites_coro, oa_related_coro, s2_match_coro
        )

        _add(oa_refs)
        _add(oa_cites)
        _add(oa_related)

        if s2_match and s2_match.s2_id:
            s2_id = s2_match.s2_id
            rec_limit = min(30, max_papers)

            s2_refs_list, s2_cites_list, s2_recs_list = await asyncio.gather(
                _fetch("Semantic Scholar references",      s2.get_references(s2_id, limit=_SOURCE_LIMIT),        []),
                _fetch("Semantic Scholar citations",       s2.get_citations(s2_id, limit=_SOURCE_LIMIT),         []),
                _fetch("Semantic Scholar recommendations", s2.get_recommendations(s2_id, limit=rec_limit),       []),
            )
            _add(s2_refs_list)
            _add(s2_cites_list)
            _add(s2_recs_list)

    finally:
        await oa.close()
        await s2.close()

    papers.sort(key=lambda p: p.citation_count or 0, reverse=True)
    papers = papers[:max_papers]

    logger.info("Total unique papers retrieved: %d (after citation-count ranking)", len(papers))
    return {"raw_papers": papers}
