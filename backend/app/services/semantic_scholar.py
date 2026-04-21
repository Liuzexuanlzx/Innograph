import httpx

from app.config import get_settings
from app.models.paper import Paper

BASE_URL = "https://api.semanticscholar.org/graph/v1"
REC_URL = "https://api.semanticscholar.org/recommendations/v1"

FIELDS = "paperId,externalIds,title,abstract,authors,year,venue,citationCount,referenceCount,fieldsOfStudy"


class SemanticScholarClient:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.s2_api_key
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            self._client = httpx.AsyncClient(timeout=30.0, headers=headers)
        return self._client

    def _parse_paper(self, data: dict) -> Paper:
        ext = data.get("externalIds") or {}
        authors = [a.get("name", "") for a in data.get("authors", []) if a.get("name")]
        return Paper(
            s2_id=data.get("paperId"),
            doi=ext.get("DOI"),
            openalex_id=None,
            title=data.get("title", ""),
            abstract=data.get("abstract"),
            authors=authors,
            publication_year=data.get("year"),
            venue=data.get("venue"),
            citation_count=data.get("citationCount", 0),
            reference_count=data.get("referenceCount", 0),
            fields_of_study=data.get("fieldsOfStudy") or [],
        )

    async def get_paper(self, paper_id: str) -> Paper | None:
        resp = await self.client.get(
            f"{BASE_URL}/paper/{paper_id}",
            params={"fields": FIELDS},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._parse_paper(resp.json())

    async def match_paper(self, query: str) -> Paper | None:
        resp = await self.client.get(
            f"{BASE_URL}/paper/search/match",
            params={"query": query, "fields": FIELDS},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        matches = resp.json().get("data", [])
        if not matches:
            return None
        return self._parse_paper(matches[0])

    async def get_citations(self, paper_id: str, limit: int = 50) -> list[Paper]:
        resp = await self.client.get(
            f"{BASE_URL}/paper/{paper_id}/citations",
            params={"fields": FIELDS, "limit": limit},
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [self._parse_paper(item["citingPaper"]) for item in data if item.get("citingPaper")]

    async def get_references(self, paper_id: str, limit: int = 50) -> list[Paper]:
        resp = await self.client.get(
            f"{BASE_URL}/paper/{paper_id}/references",
            params={"fields": FIELDS, "limit": limit},
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [
            self._parse_paper(item["citedPaper"])
            for item in data
            if item.get("citedPaper") and item["citedPaper"].get("paperId")
        ]

    async def get_recommendations(self, paper_id: str, limit: int = 10) -> list[Paper]:
        resp = await self.client.post(
            f"{REC_URL}/papers/",
            json={"positivePaperIds": [paper_id]},
            params={"fields": FIELDS, "limit": limit},
        )
        resp.raise_for_status()
        papers = resp.json().get("recommendedPapers", [])
        return [self._parse_paper(p) for p in papers]

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
