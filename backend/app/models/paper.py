from pydantic import BaseModel, Field


class Paper(BaseModel):
    openalex_id: str | None = None
    doi: str | None = None
    s2_id: str | None = None
    title: str
    abstract: str | None = None
    authors: list[str] = Field(default_factory=list)
    publication_year: int | None = None
    venue: str | None = None
    citation_count: int = 0
    reference_count: int = 0
    fields_of_study: list[str] = Field(default_factory=list)
    embedding: list[float] | None = None
    url: str | None = None


class PaperCard(BaseModel):
    """LLM-extracted structured summary of a paper."""

    paper_id: str
    short_label: str = ""
    problem: str = ""
    method_summary: str = ""
    key_modules: list[str] = Field(default_factory=list)
    claimed_gains: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)
