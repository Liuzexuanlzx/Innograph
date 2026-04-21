from typing import Annotated, TypedDict

from app.models.paper import Paper, PaperCard
from app.models.edge import InnovationEdge


def _add_list(left: list, right: list) -> list:
    return left + right


class InnoGraphState(TypedDict):
    user_input: str
    seed_paper_id: str | None
    retrieval_plan: dict
    raw_papers: Annotated[list[Paper], _add_list]
    paper_cards: Annotated[list[PaperCard], _add_list]
    paper_pairs: list[tuple[str, str]]
    candidate_edges: Annotated[list[InnovationEdge], _add_list]
    verified_edges: Annotated[list[InnovationEdge], _add_list]
    rejected_pairs: list[tuple[str, str]]
    summaries: dict
    iteration: int
    max_iterations: int
    errors: Annotated[list[str], _add_list]
