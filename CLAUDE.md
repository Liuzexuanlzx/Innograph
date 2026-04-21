# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is InnoGraph

A multi-agent innovation genealogy graph for scientific literature. Given a seed paper (DOI/title/arXiv ID), it builds an explainable graph where edges describe HOW paper B improves upon paper A, using a 3-level taxonomy with evidence spans and confidence scores.

## Commands

```bash
# Infrastructure (Neo4j + Redis)
make dev

# Backend (separate terminals)
make backend-dev          # FastAPI on :8000
make celery-dev           # Celery worker

# Frontend
make frontend-dev         # Vite on :5173

# All services via Docker
make up                   # docker compose up -d
make down

# Neo4j schema init
make seed

# Tests
make test-backend         # pytest tests/ -v
make test                 # backend + frontend
cd backend && python -m pytest tests/test_agents/test_workflow.py -v  # single test file
cd backend && python -m pytest tests/test_services/test_openalex.py::TestOpenAlexParsing::test_parse_work -v  # single test

# Lint
make lint-backend         # ruff check
```

## Architecture

**Monorepo**: `backend/` (Python 3.12, FastAPI) + `frontend/` (React 19, TypeScript, Vite)

### Backend request flow

1. `POST /api/v1/graph/build` dispatches a Celery task (`workers/graph_builder.py`)
2. Celery runs the compiled LangGraph workflow (`agents/workflow.py`) synchronously via `asyncio.new_event_loop()`
3. Frontend polls `GET /api/v1/graph/tasks/{task_id}` (2s interval) until SUCCESS
4. Frontend fetches `GET /api/v1/graph/tasks/{task_id}/snapshot` → `GraphSnapshot`

### LangGraph workflow pipeline

```
seed_planner → retrieval → paper_reader → relation_extractor → verifier → graph_summarizer → persist_graph → END
                                                                   ↑            |
                                                                   └── retry ───┘ (if rejected_pairs & iteration < max_iterations)
```

- **seed_planner**: Resolves query to OpenAlex work ID
- **retrieval**: Fetches refs/citations (OpenAlex) + recommendations (Semantic Scholar), deduplicates by title
- **paper_reader**: LLM extracts structured PaperCards from abstracts (batches of 5)
- **relation_extractor**: LLM classifies innovation edges using 3-level taxonomy (batches of 5)
- **verifier**: LLM assigns confidence scores, filters < 0.5 as UNSUPPORTED (batches of 5)
- **graph_summarizer**: LLM generates lineage narratives
- **persist_graph**: Writes to Neo4j

State fields annotated with `_add_list` (raw_papers, paper_cards, candidate_edges, verified_edges, errors) accumulate across nodes rather than overwrite.

### 3-level edge taxonomy (`models/edge.py`)

- **L1 RelationType** (9): IMPROVES_ON, EXTENDS, COMBINES_WITH, APPLIES_TO, SIMPLIFIES, GENERALIZES, PROVIDES_THEORY_FOR, REPRODUCES, CONTRADICTS
- **L2 InnovationDimension** (14): ACCURACY, EFFICIENCY, SCALABILITY, etc.
- **L3 Operation** (15): ADDS_MODULE, REPLACES_BACKBONE, CHANGES_LOSS_FUNCTION, etc.

All three levels are Python `str, Enum` and mirrored as TypeScript union types in `frontend/src/api/types.ts`.

### Key domain model relationships

`GraphSnapshot` is the primary frontend payload: contains `Paper[]`, `PaperCard[]`, `InnovationEdge[]`, and `summaries`. PaperCard links to Paper via `paper_id` (= `openalex_id`). InnovationEdge connects two papers via `source_paper_id`/`target_paper_id`.

### Services layer

- **LLMProvider** (`services/llm_provider.py`): OpenAI GPT-4o primary, Anthropic fallback. Uses langchain's `with_structured_output()` for typed responses.
- **OpenAlexClient**: Reconstructs abstracts from inverted index format. Polite pool via `mailto` param.
- **SemanticScholarClient**: Optional API key for higher rate limits (100 req/s vs 1 req/s).
- **Neo4jService**: Async driver. Papers use MERGE on `openalex_id`; edges use CREATE with `randomUUID()`. Edge evidence stored as JSON string in `evidence_json` property.
- **CacheService**: Redis with TTL 24h (API responses) / 7d (LLM extractions). Key patterns: `paper_card:{id}`, `edge:{src}:{tgt}`, `api:{key}`.

### Frontend architecture

- **State**: Zustand stores (`graphStore` for snapshot/selection/layout, `taskStore` for polling)
- **Graph viz**: Cytoscape.js via `useCytoscape` hook. Nodes colored by year, sized by citation count. Edges colored by L1 relation type, opacity by confidence.
- **Proxy**: Vite proxies `/api` to `http://localhost:8000`

### LLM prompts

Jinja2 templates in `backend/app/prompts/`. Each agent's prompt is loaded at runtime via `Path(__file__).parent.parent / "prompts" / "<name>.txt"`. The relation_extractor prompt includes the full L1/L2/L3 taxonomy as reference for the LLM.

## Configuration

All backend config via Pydantic Settings in `app/config.py`, loaded from `.env`. Key vars: `NEO4J_URI`, `REDIS_URL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENALEX_EMAIL`, `S2_API_KEY`, `CORS_ORIGINS`.

## Testing

Backend uses pytest with `asyncio_mode = "auto"`. HTTP mocking via `pytest-httpx`. Fixtures in `tests/conftest.py` provide `client` (FastAPI TestClient), `sample_openalex_work`, `sample_s2_paper`. JSON fixtures in `tests/fixtures/`.

## Docker topology

neo4j:5 (:7474/:7687) + redis:7-alpine (:6379) → backend (FastAPI :8000) + celery_worker (concurrency=2) → frontend (Vite :5173). Backend and celery_worker share the same image, differ only in CMD.
