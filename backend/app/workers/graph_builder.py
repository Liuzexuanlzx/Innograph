import asyncio
import logging

from celery import Celery

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
celery_app = Celery("innograph", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    task_track_started=True,
)


@celery_app.task(bind=True, name="innograph.build_graph")
def build_innovation_graph(self, query: str, depth: int = 1, max_papers: int = 40, min_confidence: float = 0.5):
    """Celery task that runs the LangGraph workflow."""
    from app.agents.workflow import compile_workflow

    logger.info(
        "Starting graph build query=%r depth=%s max_papers=%s min_confidence=%s",
        query,
        depth,
        max_papers,
        min_confidence,
    )
    def report_progress(message: str) -> None:
        self.update_state(state="RUNNING", meta={"progress": message})

    report_progress("Compiling workflow...")
    workflow = compile_workflow(progress_callback=report_progress)

    initial_state = {
        "user_input": query,
        "seed_paper_id": None,
        "retrieval_plan": {"max_papers": max_papers, "depth": depth},
        "raw_papers": [],
        "paper_cards": [],
        "paper_pairs": [],
        "candidate_edges": [],
        "verified_edges": [],
        "rejected_pairs": [],
        "summaries": {},
        "iteration": 0,
        "max_iterations": 2,
        "errors": [],
    }

    report_progress("Starting workflow...")

    # Run the async workflow in a sync context
    loop = asyncio.new_event_loop()
    try:
        final_state = loop.run_until_complete(workflow.ainvoke(initial_state))
    except Exception:
        logger.exception("Graph build failed for query=%r", query)
        raise
    finally:
        loop.close()

    # Filter edges by min_confidence
    verified = final_state.get("verified_edges", [])
    filtered = [e for e in verified if e.confidence >= min_confidence]

    # Build snapshot result
    papers = final_state.get("raw_papers", [])
    paper_cards = final_state.get("paper_cards", [])
    summaries = final_state.get("summaries", {})

    logger.info(
        "Graph build finished query=%r papers=%d paper_cards=%d verified_edges=%d filtered_edges=%d",
        query,
        len(papers),
        len(paper_cards),
        len(verified),
        len(filtered),
    )

    return {
        "papers": [p.model_dump() for p in papers],
        "paper_cards": [c.model_dump() for c in paper_cards],
        "innovation_edges": [e.model_dump() for e in filtered],
        "summaries": summaries,
        "seed_paper_id": final_state.get("seed_paper_id"),
    }
