import httpx

from app.config import get_settings
from app.models.paper import Paper

BASE_URL = "https://api.openalex.org"
AUTOCOMPLETE_URL = "https://api.openalex.org/autocomplete/works"


class OpenAlexClient:
    def __init__(self):
        settings = get_settings()
        self.email = settings.openalex_email
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _params(self, extra: dict | None = None) -> dict:
        params = {}
        if self.email:
            params["mailto"] = self.email
        if extra:
            params.update(extra)
        return params

    def _parse_work(self, work: dict) -> Paper:
        authors = []
        for authorship in work.get("authorships", []):
            name = authorship.get("author", {}).get("display_name")
            if name:
                authors.append(name)

        abstract = work.get("abstract_inverted_index")
        abstract_text = None
        if abstract:
            # Reconstruct abstract from inverted index
            word_positions: list[tuple[int, str]] = []
            for word, positions in abstract.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract_text = " ".join(w for _, w in word_positions)

        return Paper(
            openalex_id=work.get("id", "").replace("https://openalex.org/", ""),
            doi=work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else None,
            title=work.get("title", ""),
            abstract=abstract_text,
            authors=authors,
            publication_year=work.get("publication_year"),
            venue=work.get("primary_location", {}).get("source", {}).get("display_name")
            if work.get("primary_location") and work["primary_location"].get("source")
            else None,
            citation_count=work.get("cited_by_count", 0),
            reference_count=len(work.get("referenced_works", [])),
            fields_of_study=[
                c.get("display_name", "")
                for c in work.get("concepts", [])[:5]
            ],
            url=work.get("doi") or work.get("id"),
        )

    async def search_works(self, query: str, per_page: int = 10) -> list[Paper]:
        resp = await self.client.get(
            f"{BASE_URL}/works",
            params=self._params({"search": query, "per_page": per_page}),
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [self._parse_work(w) for w in results]

    async def autocomplete_works(self, query: str, per_page: int = 5) -> list[str]:
        resp = await self.client.get(
            AUTOCOMPLETE_URL,
            params={"q": query},
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        work_ids = []
        for item in results:
            work_id = item.get("id", "").replace("https://openalex.org/", "")
            if work_id:
                work_ids.append(work_id)
        return work_ids

    async def get_work(self, work_id: str) -> Paper | None:
        resp = await self.client.get(
            f"{BASE_URL}/works/{work_id}",
            params=self._params(),
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._parse_work(resp.json())

    async def get_references(self, work_id: str, per_page: int = 50) -> list[Paper]:
        resp = await self.client.get(
            f"{BASE_URL}/works",
            params=self._params({
                "filter": f"cited_by:{work_id}",
                "per_page": per_page,
            }),
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [self._parse_work(w) for w in results]

    async def get_citations(self, work_id: str, per_page: int = 50) -> list[Paper]:
        resp = await self.client.get(
            f"{BASE_URL}/works",
            params=self._params({
                "filter": f"cites:{work_id}",
                "per_page": per_page,
            }),
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [self._parse_work(w) for w in results]

    async def get_related_works(self, work_id: str) -> list[Paper]:
        work_resp = await self.client.get(
            f"{BASE_URL}/works/{work_id}",
            params=self._params(),
        )
        work_resp.raise_for_status()
        related_ids = work_resp.json().get("related_works", [])[:10]
        papers = []
        for rid in related_ids:
            oa_id = rid.replace("https://openalex.org/", "")
            paper = await self.get_work(oa_id)
            if paper:
                papers.append(paper)
        return papers

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
