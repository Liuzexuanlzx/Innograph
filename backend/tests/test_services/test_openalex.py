import json
from pathlib import Path

import pytest
import httpx

from app.services.openalex import OpenAlexClient

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def oa_client():
    return OpenAlexClient()


class TestOpenAlexParsing:
    def test_parse_work(self, oa_client, sample_openalex_work):
        paper = oa_client._parse_work(sample_openalex_work)
        assert paper.title == "Attention Is All You Need"
        assert paper.openalex_id == "W2741809807"
        assert paper.doi == "10.48550/arXiv.1706.03762"
        assert paper.publication_year == 2017
        assert paper.citation_count == 90000
        assert "Ashish Vaswani" in paper.authors
        assert paper.venue == "NeurIPS"
        assert paper.abstract is not None
        assert "dominant" in paper.abstract

    def test_parse_work_no_abstract(self, oa_client):
        work = {"id": "https://openalex.org/W123", "title": "Test", "authorships": []}
        paper = oa_client._parse_work(work)
        assert paper.abstract is None
        assert paper.title == "Test"


@pytest.mark.asyncio
async def test_search_works(httpx_mock, oa_client):
    fixture = json.loads((FIXTURES / "openalex_search.json").read_text())
    httpx_mock.add_response(
        url=httpx.URL(
            "https://api.openalex.org/works",
            params={
                "mailto": oa_client.email,
                "search": "attention",
                "per_page": "10",
            },
        ),
        json=fixture,
    )
    results = await oa_client.search_works("attention")
    assert len(results) == 1
    assert results[0].title == "Attention Is All You Need"
    await oa_client.close()


@pytest.mark.asyncio
async def test_autocomplete_works(httpx_mock, oa_client):
    httpx_mock.add_response(
        url=httpx.URL("https://api.openalex.org/autocomplete/works", params={"q": "ReAct"}),
        json={
            "results": [
                {"id": "https://openalex.org/W6891747626"},
                {"id": "https://openalex.org/W6948057579"},
            ]
        },
    )
    results = await oa_client.autocomplete_works("ReAct", per_page=5)
    assert results == ["W6891747626", "W6948057579"]
    await oa_client.close()
