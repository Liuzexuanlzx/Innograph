import asyncio
import logging
import re
from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel, Field

from app.agents.state import InnoGraphState
from app.models.paper import PaperCard
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "paper_reader.txt"


class PaperCardOutput(BaseModel):
    short_label: str = ""
    problem: str = ""
    method_summary: str = ""
    key_modules: list[str] = Field(default_factory=list)
    claimed_gains: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "towards",
    "with",
}


def _clean_short_label(label: str) -> str:
    cleaned = " ".join(label.replace("\n", " ").split()).strip(" -:;,")
    if len(cleaned) > 28:
        return cleaned[:28].rstrip()
    return cleaned


def infer_short_label_from_title(title: str) -> str:
    clean_title = " ".join(title.split()).strip()
    if not clean_title:
        return ""

    if ":" in clean_title:
        prefix = clean_title.split(":", 1)[0].strip()
        if prefix and len(prefix) <= 28 and len(prefix.split()) <= 4:
            return _clean_short_label(prefix)

    paren_tokens = [token.strip() for token in re.findall(r"\(([A-Za-z][A-Za-z0-9-]{1,18})\)", clean_title)]
    for token in paren_tokens:
        if len(token) <= 18:
            return _clean_short_label(token)

    acronym_tokens = []
    for token in clean_title.replace("/", " ").split():
        stripped = token.strip(" ,.;:()[]{}")
        if not stripped:
            continue
        if stripped.isupper() and 2 <= len(stripped) <= 10:
            return _clean_short_label(stripped)
        if any(char.isupper() for char in stripped[1:]) and len(stripped) <= 18:
            return _clean_short_label(stripped)
        if stripped[0].isalpha() and stripped[0].isupper() and stripped.lower() not in STOPWORDS:
            acronym_tokens.append(stripped[0].upper())

    acronym = "".join(acronym_tokens[:6])
    if 2 <= len(acronym) <= 8:
        return acronym

    keywords = [
        token.strip(" ,.;:()[]{}")
        for token in clean_title.split()
        if token.strip(" ,.;:()[]{}") and token.strip(" ,.;:()[]{}").lower() not in STOPWORDS
    ]
    fallback = " ".join(keywords[:2])
    return _clean_short_label(fallback)


def resolve_short_label(title: str, candidate: str) -> str:
    cleaned = _clean_short_label(candidate)
    if cleaned:
        return cleaned
    return infer_short_label_from_title(title)


async def paper_reader(state: InnoGraphState) -> dict:
    """Extract structured paper cards from raw papers using LLM."""
    raw_papers = state.get("raw_papers", [])
    if not raw_papers:
        return {"errors": ["No papers to read"]}

    llm = LLMProvider()
    template = Template(PROMPT_PATH.read_text())
    cards = []

    async def _read_one(paper) -> PaperCard | None:
        if not paper.abstract:
            # Skip papers without abstract — empty cards degrade relation extraction quality
            logger.debug("Skipping paper without abstract: %s", paper.title)
            return None
        prompt = template.render(title=paper.title, abstract=paper.abstract)
        try:
            result = await llm.complete(
                [{"role": "user", "content": prompt}],
                response_model=PaperCardOutput,
            )
            return PaperCard(
                paper_id=paper.openalex_id or paper.s2_id or "",
                short_label=resolve_short_label(paper.title, result.short_label),
                problem=result.problem,
                method_summary=result.method_summary,
                key_modules=result.key_modules,
                claimed_gains=result.claimed_gains,
                limitations=result.limitations,
                datasets=result.datasets,
                baselines=result.baselines,
            )
        except Exception as e:
            logger.warning("Failed to read paper %s: %s", paper.title, e)
            return None

    # Process all papers fully concurrently (DeepSeek has no strict rate limit)
    results = await asyncio.gather(*[_read_one(p) for p in raw_papers])
    cards = [c for c in results if c is not None]

    logger.info("Extracted %d paper cards", len(cards))
    return {"paper_cards": cards}
