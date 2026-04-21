import pytest

from app.agents import seed_planner as seed_module
from app.models.paper import Paper


class FakeOpenAlexClient:
    async def get_work(self, work_id: str):
        if work_id == "W6891747626":
            return Paper(
                openalex_id="W6891747626",
                doi="10.48448/gfg3-ga94",
                title="ReAct: Synergizing Reasoning and Acting in Language Models",
            )
        return None

    async def autocomplete_works(self, query: str, per_page: int = 5):
        if query == "ReAct: Synergizing Reasoning and Acting in Language Models":
            return ["W6891747626"]
        return []

    async def search_works(self, query: str, per_page: int = 5):
        return []

    async def close(self):
        return None


def test_extract_arxiv_id():
    assert seed_module._extract_arxiv_id("https://arxiv.org/abs/2210.03629") == "2210.03629"
    assert seed_module._extract_arxiv_id("https://arxiv.org/pdf/2210.03629.pdf") == "2210.03629"
    assert seed_module._extract_arxiv_id("arXiv:2210.03629") == "2210.03629"
    assert seed_module._extract_arxiv_id("2210.03629") == "2210.03629"


@pytest.mark.asyncio
async def test_seed_planner_resolves_arxiv_url(monkeypatch):
    async def fake_fetch_title(arxiv_id: str):
        assert arxiv_id == "2210.03629"
        return "ReAct: Synergizing Reasoning and Acting in Language Models"

    monkeypatch.setattr(seed_module, "OpenAlexClient", FakeOpenAlexClient)
    monkeypatch.setattr(seed_module, "_fetch_arxiv_title", fake_fetch_title)

    state = {
        "user_input": "https://arxiv.org/abs/2210.03629",
        "seed_paper_id": None,
        "retrieval_plan": {"max_papers": 10, "depth": 1},
        "raw_papers": [],
    }

    result = await seed_module.seed_planner(state)

    assert result["seed_paper_id"] == "W6891747626"
    assert result["raw_papers"][0].title == "ReAct: Synergizing Reasoning and Acting in Language Models"
