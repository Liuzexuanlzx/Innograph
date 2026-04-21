import pytest

from app.agents import retrieval as retrieval_module
from app.models.paper import Paper


SEED_PAPER = Paper(
    openalex_id="W6891747626",
    doi="10.48448/gfg3-ga94",
    title="ReAct: Synergizing Reasoning and Acting in Language Models",
)


class FakeOpenAlexClient:
    async def get_references(self, work_id: str, per_page: int = 50):
        assert work_id == "W6891747626"
        return []

    async def get_citations(self, work_id: str, per_page: int = 50):
        assert work_id == "W6891747626"
        return []

    async def get_related_works(self, work_id: str):
        assert work_id == "W6891747626"
        return []

    async def close(self):
        return None


class FakeSemanticScholarClient:
    async def match_paper(self, query: str):
        assert query == SEED_PAPER.title
        return Paper(
            s2_id="S2-REACT",
            title=SEED_PAPER.title,
        )

    async def get_references(self, paper_id: str, limit: int = 50):
        assert paper_id == "S2-REACT"
        return [
            Paper(
                s2_id="S2-REF-1",
                title="Faithful Reasoning Using Large Language Models",
            )
        ]

    async def get_citations(self, paper_id: str, limit: int = 50):
        assert paper_id == "S2-REACT"
        return [
            Paper(
                s2_id="S2-CITE-1",
                title="Neuro-symbolic agentic AI: Architectures, integration patterns, applications, open challenges and future research directions",
            )
        ]

    async def get_recommendations(self, paper_id: str, limit: int = 10):
        assert paper_id == "S2-REACT"
        return [
            Paper(
                s2_id="S2-REF-1-DUP",
                title="Faithful Reasoning Using Large Language Models",
            ),
            Paper(
                s2_id="S2-REC-1",
                title="Toolformer: Language Models Can Teach Themselves to Use Tools",
            ),
        ]

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_retrieval_falls_back_to_semantic_scholar(monkeypatch):
    monkeypatch.setattr(retrieval_module, "OpenAlexClient", FakeOpenAlexClient)
    monkeypatch.setattr(retrieval_module, "SemanticScholarClient", FakeSemanticScholarClient)

    state = {
        "user_input": "https://arxiv.org/abs/2210.03629",
        "seed_paper_id": "W6891747626",
        "retrieval_plan": {"max_papers": 5, "depth": 1},
        "raw_papers": [SEED_PAPER],
    }

    result = await retrieval_module.retrieval(state)

    titles = [paper.title for paper in result["raw_papers"]]
    assert titles == [
        "Faithful Reasoning Using Large Language Models",
        "Neuro-symbolic agentic AI: Architectures, integration patterns, applications, open challenges and future research directions",
        "Toolformer: Language Models Can Teach Themselves to Use Tools",
    ]
