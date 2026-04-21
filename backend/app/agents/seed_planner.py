import logging
import re
import xml.etree.ElementTree as ET

import httpx

from app.agents.state import InnoGraphState
from app.services.openalex import OpenAlexClient

logger = logging.getLogger(__name__)

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_ID_RE = re.compile(
    r"(?:(?:https?://)?arxiv\.org/(?:abs|pdf)/|arxiv:)?(?P<id>\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?/?$",
    re.IGNORECASE,
)


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _extract_arxiv_id(user_input: str) -> str | None:
    match = ARXIV_ID_RE.search(user_input.strip())
    if match:
        return match.group("id")
    return None


async def _fetch_arxiv_title(arxiv_id: str) -> str | None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(ARXIV_API_URL, params={"id_list": arxiv_id})
        resp.raise_for_status()

    root = ET.fromstring(resp.text)
    title = root.findtext("atom:entry/atom:title", default="", namespaces=ATOM_NS)
    title = " ".join(title.split())
    return title or None


async def _resolve_openalex_by_title(client: OpenAlexClient, title: str):
    normalized_title = _normalize_title(title)

    candidate_ids = await client.autocomplete_works(title, per_page=5)
    fallback = None

    for work_id in candidate_ids:
        paper = await client.get_work(work_id)
        if not paper:
            continue
        if fallback is None:
            fallback = paper
        if _normalize_title(paper.title) == normalized_title:
            return paper

    results = await client.search_works(title, per_page=5)
    for paper in results:
        if _normalize_title(paper.title) == normalized_title:
            return paper

    if results:
        return results[0]
    return fallback


def _seed_response(state: InnoGraphState, paper):
    return {
        "seed_paper_id": paper.openalex_id,
        "raw_papers": [paper],
        "retrieval_plan": {
            "strategy": "citation_tree",
            "depth": 1,
            "max_papers": state.get("retrieval_plan", {}).get("max_papers", 30),
        },
    }


async def seed_planner(state: InnoGraphState) -> dict:
    """Resolve user input to a seed paper via OpenAlex search."""
    user_input = state["user_input"]
    logger.info("Seed planner: resolving '%s'", user_input)

    client = OpenAlexClient()
    try:
        # Try as DOI first
        if user_input.startswith("10.") or "doi.org" in user_input:
            doi = user_input.replace("https://doi.org/", "").replace("http://doi.org/", "")
            paper = await client.get_work(f"doi:{doi}")
            if paper:
                return _seed_response(state, paper)

        arxiv_id = _extract_arxiv_id(user_input)
        if arxiv_id:
            try:
                arxiv_title = await _fetch_arxiv_title(arxiv_id)
            except Exception as e:
                logger.warning("Failed to resolve arXiv title for %s: %s", arxiv_id, e)
                arxiv_title = None

            if arxiv_title:
                paper = await _resolve_openalex_by_title(client, arxiv_title)
                if paper:
                    return _seed_response(state, paper)

        # Fall back to title search
        paper = await _resolve_openalex_by_title(client, user_input)
        if not paper:
            return {"errors": [f"No papers found for query: {user_input}"]}

        return _seed_response(state, paper)
    finally:
        await client.close()
