import pytest
import httpx

from app.services.semantic_scholar import SemanticScholarClient


class TestS2Parsing:
    def test_parse_paper(self, sample_s2_paper):
        client = SemanticScholarClient()
        paper = client._parse_paper(sample_s2_paper)
        assert paper.title == "Attention Is All You Need"
        assert paper.s2_id == "abc123"
        assert paper.doi == "10.48550/arXiv.1706.03762"
        assert paper.publication_year == 2017
        assert "Ashish Vaswani" in paper.authors
        assert paper.citation_count == 90000


@pytest.mark.asyncio
async def test_match_paper(httpx_mock, sample_s2_paper):
    client = SemanticScholarClient()
    httpx_mock.add_response(
        url=httpx.URL(
            "https://api.semanticscholar.org/graph/v1/paper/search/match",
            params={
                "query": "ReAct: Synergizing Reasoning and Acting in Language Models",
                "fields": (
                    "paperId,externalIds,title,abstract,authors,year,venue,"
                    "citationCount,referenceCount,fieldsOfStudy"
                ),
            },
        ),
        json={"data": [sample_s2_paper]},
    )

    paper = await client.match_paper("ReAct: Synergizing Reasoning and Acting in Language Models")

    assert paper is not None
    assert paper.title == "Attention Is All You Need"
    await client.close()
