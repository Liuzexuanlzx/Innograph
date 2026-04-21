import logging
from pathlib import Path

from jinja2 import Template
from pydantic import BaseModel

from app.agents.state import InnoGraphState
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "graph_summarizer.txt"


class GraphSummaryOutput(BaseModel):
    lineage_summary: str = ""
    branch_summaries: list[str] = []
    seed_innovation_summary: str = ""


async def graph_summarizer(state: InnoGraphState) -> dict:
    """Generate narrative summaries of the innovation graph."""
    verified_edges = state.get("verified_edges", [])
    paper_cards = state.get("paper_cards", [])
    seed_id = state.get("seed_paper_id")

    if not verified_edges:
        return {
            "summaries": {
                "lineage_summary": "No verified innovation edges found.",
                "branch_summaries": [],
                "seed_innovation_summary": "",
            }
        }

    llm = LLMProvider()
    template = Template(PROMPT_PATH.read_text())

    card_map = {c.paper_id: c for c in paper_cards}
    edges_data = [
        {
            "source": e.source_paper_id,
            "target": e.target_paper_id,
            "relation": e.relation_type.value,
            "dimensions": [d.value for d in e.innovation_dimensions],
            "summary": e.summary,
            "confidence": e.confidence,
        }
        for e in verified_edges
    ]

    prompt = template.render(
        seed_id=seed_id,
        edges=edges_data,
        paper_cards={pid: c.model_dump() for pid, c in card_map.items()},
    )

    try:
        result = await llm.complete(
            [{"role": "user", "content": prompt}],
            response_model=GraphSummaryOutput,
        )
        return {
            "summaries": {
                "lineage_summary": result.lineage_summary,
                "branch_summaries": result.branch_summaries,
                "seed_innovation_summary": result.seed_innovation_summary,
            }
        }
    except Exception as e:
        logger.error("Graph summarization failed: %s", e)
        return {
            "summaries": {"lineage_summary": "Summarization failed.", "branch_summaries": []},
            "errors": [f"Summarization error: {e}"],
        }
