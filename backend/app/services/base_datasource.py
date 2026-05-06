import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List

from app.models.paper import Paper


class BaseDatasource(ABC):
    """Abstract base class for academic paper data sources."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the datasource."""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Priority level (lower = higher priority)."""
        pass
    
    @abstractmethod
    async def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        """Search papers by query string."""
        pass
    
    @abstractmethod
    async def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """Get paper by datasource-specific ID."""
        pass
    
    @abstractmethod
    async def get_paper_by_doi(self, doi: str) -> Optional[Paper]:
        """Get paper by DOI."""
        pass
    
    @abstractmethod
    async def get_citations(self, paper_id: str, limit: int = 50) -> List[Paper]:
        """Get papers citing the given paper."""
        pass
    
    @abstractmethod
    async def get_references(self, paper_id: str, limit: int = 50) -> List[Paper]:
        """Get papers referenced by the given paper."""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources."""
        pass


class DatasourceManager:
    """Manager for coordinating multiple datasources."""
    
    def __init__(self):
        self._datasources: List[BaseDatasource] = []
    
    def register(self, datasource: BaseDatasource):
        """Register a datasource."""
        self._datasources.append(datasource)
        self._datasources.sort(key=lambda x: x.priority)
    
    async def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        """Search across all registered datasources."""
        results = []
        seen_titles = set()
        
        for ds in self._datasources:
            try:
                papers = await ds.search_papers(query, limit)
                for p in papers:
                    title_key = (p.title or "").lower().strip()
                    if title_key and title_key not in seen_titles:
                        seen_titles.add(title_key)
                        results.append(p)
                        if len(results) >= limit:
                            return results
            except Exception as e:
                print(f"Error from {ds.name}: {e}")
                continue
        
        return results
    
    async def get_paper_by_doi(self, doi: str) -> Optional[Paper]:
        """Get paper by DOI, trying datasources in priority order."""
        for ds in self._datasources:
            try:
                paper = await ds.get_paper_by_doi(doi)
                if paper:
                    return paper
            except Exception as e:
                print(f"Error from {ds.name}: {e}")
                continue
        return None
    
    async def close_all(self):
        """Close all datasources."""
        await asyncio.gather(*[ds.close() for ds in self._datasources])
