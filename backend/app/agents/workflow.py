import logging
from collections.abc import Awaitable, Callable

from langgraph.graph import StateGraph, END

from app.agents.state import InnoGraphState
from app.agents.seed_planner import seed_planner
from app.agents.retrieval import retrieval
from app.agents.paper_reader import paper_reader
from app.agents.relation_extractor import relation_extractor
from app.agents.verifier import verifier
from app.agents.graph_summarizer import graph_summarizer
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

NodeFn = Callable[[InnoGraphState], Awaitable[dict]]


def _with_progress(
    name: str,
    label: str,
    fn: NodeFn,
    progress_callback: Callable[[str], None] | None = None,
) -> NodeFn:
    async def wrapped(state: InnoGraphState) -> dict:
        if progress_callback:
            progress_callback(label)
        logger.info("Workflow step: %s", name)
        return await fn(state)

    return wrapped


async def persist_graph(state: InnoGraphState) -> dict:
    """Write all papers and verified edges to Neo4j."""
    neo4j = Neo4jService()
    try:
        for paper in state.get("raw_papers", []):
            if paper.openalex_id:
                await neo4j.upsert_paper(paper)

        for card in state.get("paper_cards", []):
            await neo4j.upsert_paper_card(card)

        for edge in state.get("verified_edges", []):
            await neo4j.upsert_innovation_edge(edge)

        logger.info("Persisted graph to Neo4j")
    finally:
        await neo4j.close()
    return {}


def should_retry(state: InnoGraphState) -> str:
    """Decide whether to retry relation extraction for rejected pairs."""
    rejected = state.get("rejected_pairs", [])
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", 2)

    if rejected and iteration < max_iter:
        return "retry"
    return "continue"


def build_workflow(progress_callback: Callable[[str], None] | None = None) -> StateGraph:
    """Build and compile the InnoGraph LangGraph workflow."""
    workflow = StateGraph(InnoGraphState)

    workflow.add_node(
        "seed_planner",
        _with_progress(
            "seed_planner",
            "Resolving seed paper...",
            seed_planner,
            progress_callback,
        ),
    )
    workflow.add_node(
        "retrieval",
        _with_progress(
            "retrieval",
            "Retrieving related papers...",
            retrieval,
            progress_callback,
        ),
    )
    workflow.add_node(
        "paper_reader",
        _with_progress(
            "paper_reader",
            "Reading papers with LLM...",
            paper_reader,
            progress_callback,
        ),
    )
    workflow.add_node(
        "relation_extractor",
        _with_progress(
            "relation_extractor",
            "Extracting innovation relations...",
            relation_extractor,
            progress_callback,
        ),
    )
    workflow.add_node(
        "verifier",
        _with_progress(
            "verifier",
            "Verifying candidate edges...",
            verifier,
            progress_callback,
        ),
    )
    workflow.add_node(
        "graph_summarizer",
        _with_progress(
            "graph_summarizer",
            "Summarizing graph...",
            graph_summarizer,
            progress_callback,
        ),
    )
    workflow.add_node(
        "persist_graph",
        _with_progress(
            "persist_graph",
            "Persisting graph to Neo4j...",
            persist_graph,
            progress_callback,
        ),
    )

    workflow.set_entry_point("seed_planner")
    workflow.add_edge("seed_planner", "retrieval")
    workflow.add_edge("retrieval", "paper_reader")
    workflow.add_edge("paper_reader", "relation_extractor")
    workflow.add_edge("relation_extractor", "verifier")

    workflow.add_conditional_edges(
        "verifier",
        should_retry,
        {
            "retry": "relation_extractor",
            "continue": "graph_summarizer",
        },
    )

    workflow.add_edge("graph_summarizer", "persist_graph")
    workflow.add_edge("persist_graph", END)

    return workflow


def compile_workflow(progress_callback: Callable[[str], None] | None = None):
    """Return a compiled runnable workflow."""
    return build_workflow(progress_callback=progress_callback).compile()
