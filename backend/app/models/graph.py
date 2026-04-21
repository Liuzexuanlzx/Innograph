from pydantic import BaseModel, Field

from app.models.paper import Paper, PaperCard
from app.models.edge import InnovationEdge


class GraphSnapshot(BaseModel):
    """Full subgraph payload for the frontend."""

    papers: list[Paper] = Field(default_factory=list)
    paper_cards: list[PaperCard] = Field(default_factory=list)
    innovation_edges: list[InnovationEdge] = Field(default_factory=list)
    summaries: dict = Field(default_factory=dict)
    seed_paper_id: str | None = None
