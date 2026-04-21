# InnoGraph

Multi-agent innovation genealogy graph for scientific literature exploration.

Unlike citation graphs, InnoGraph builds **explainable innovation lineage** — edges that describe *how* paper B improves upon paper A, with evidence spans and confidence scores.

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys

# 2. Start all services
docker compose up -d

# 3. Initialize Neo4j schema
make seed

# 4. Open the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
```

## Development

```bash
# Start infrastructure only
make dev

# Run backend (separate terminal)
make backend-dev

# Run Celery worker (separate terminal)
make celery-dev

# Run frontend (separate terminal)
make frontend-dev

# Run tests
make test
```

## Architecture

InnoGraph uses a multi-agent LangGraph workflow:

1. **Seed Planner** — resolves user query to a seed paper
2. **Retrieval Agent** — fetches references, citations, and related works from OpenAlex + Semantic Scholar
3. **Paper Reader** — extracts structured paper cards (problem, method, contributions) via LLM
4. **Relation Extractor** — identifies innovation relationships using a 3-level taxonomy (L1: relation type, L2: innovation dimension, L3: operation)
5. **Verifier** — validates edges with confidence scoring, rejects hallucinated relationships
6. **Graph Summarizer** — generates lineage narratives

## Tech Stack

- **Backend**: FastAPI + LangGraph + Celery
- **Data Sources**: OpenAlex API + Semantic Scholar API
- **Graph DB**: Neo4j (with vector indexes)
- **LLM**: OpenAI GPT-4o (Anthropic fallback)
- **Frontend**: React 19 + TypeScript + Vite + Cytoscape.js + Zustand + Tailwind CSS

## License

MIT
