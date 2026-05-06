import httpx

from app.models.paper import Paper
from app.services.base_datasource import BaseDatasource

BASE_URL = "https://api.crossref.org"


class CrossRefClient(BaseDatasource):
    @property
    def name(self) -> str:
        return "CrossRef"

    @property
    def priority(self) -> int:
        return 3

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _parse_work(self, work: dict) -> Paper:
        authors = []
        for author in work.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if given or family:
                authors.append(f"{given} {family}".strip())

        return Paper(
            doi=work.get("DOI"),
            title=work.get("title", [""])[0] if isinstance(work.get("title"), list) else work.get("title", ""),
            abstract=None,
            authors=authors,
            publication_year=work.get("published-print", {}).get("year") or work.get("published-online", {}).get("year"),
            venue=work.get("container-title", [""])[0] if isinstance(work.get("container-title"), list) else work.get("container-title", ""),
            citation_count=work.get("is-referenced-by-count", 0),
            reference_count=0,
            fields_of_study=[],
            url=work.get("URL"),
        )

    async def search_papers(self, query: str, limit: int = 10) -> list[Paper]:
        resp = await self.client.get(
            f"{BASE_URL}/works",
            params={"query": query, "rows": limit},
        )
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])
        return [self._parse_work(item) for item in items]

    async def get_paper_by_id(self, paper_id: str) -> Paper | None:
        if paper_id.startswith("10."):
            return await self.get_paper_by_doi(paper_id)
        try:
            resp = await self.client.get(f"{BASE_URL}/works/{paper_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return self._parse_work(resp.json().get("message", {}))
        except Exception:
            return None

    async def get_paper_by_doi(self, doi: str) -> Paper | None:
        try:
            resp = await self.client.get(f"{BASE_URL}/works/{doi}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return self._parse_work(resp.json().get("message", {}))
        except Exception:
            return None

    async def get_citations(self, paper_id: str, limit: int = 50) -> list[Paper]:
        return []

    async def get_references(self, paper_id: str, limit: int = 50) -> list[Paper]:
        return []

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
