from fastapi import APIRouter, HTTPException, Query

from app.models.paper import Paper
from app.services.openalex import OpenAlexClient

router = APIRouter()


@router.get("/search")
async def search_papers(q: str = Query(..., min_length=2)) -> list[Paper]:
    """Search papers via OpenAlex."""
    client = OpenAlexClient()
    try:
        results = await client.search_works(q, per_page=10)
        return results
    finally:
        await client.close()


@router.get("/{paper_id}")
async def get_paper(paper_id: str) -> Paper:
    """Get a single paper by OpenAlex ID."""
    client = OpenAlexClient()
    try:
        paper = await client.get_work(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
    finally:
        await client.close()
