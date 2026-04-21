# InnoGraph — Roadmap

## MVP (v0.1) ✅

- [x] LangGraph multi-agent workflow (7 nodes with retry loop)
- [x] 3-level edge taxonomy (9 RelationType × 14 InnovationDimension × 15 Operation)
- [x] Evidence spans with confidence scoring and verdict
- [x] OpenAlex + Semantic Scholar integration
- [x] PaperCard structured extraction
- [x] Neo4j persistence (MERGE papers, CREATE edges)
- [x] Redis caching (24h API / 7d LLM)
- [x] FastAPI REST API (build, poll, snapshot, search, edge CRUD)
- [x] Celery async task processing
- [x] React + Cytoscape.js interactive graph visualization
- [x] Zustand state management with polling
- [x] Docker Compose full-stack deployment

## v0.2 — Depth & Quality

- [ ] Multi-hop graph expansion (depth > 1 with iterative retrieval)
- [ ] Full-text PDF ingestion via GROBID for richer evidence extraction
- [ ] Cross-paper citation context analysis
- [ ] Batch verification with inter-annotator agreement metrics
- [ ] Edge conflict detection (contradictory classifications)
- [ ] Improved deduplication using DOI + title + author fuzzy matching

## v0.3 — Interaction & Collaboration

- [ ] User accounts and saved graph sessions
- [ ] Collaborative annotation — multiple users correct edges
- [ ] Graph diff view (compare snapshots over time)
- [ ] Export to standard formats (GraphML, JSON-LD, BibTeX)
- [ ] Notification system for graph build completion
- [ ] Natural language graph query ("How did attention mechanisms evolve?")

## v1.0 — Scale & Intelligence

- [ ] Streaming workflow progress via WebSocket (replace polling)
- [ ] Scheduled re-indexing of tracked paper lineages
- [ ] Fine-tuned classification model trained on human-corrected edges
- [ ] Multi-language abstract support
- [ ] Public API with rate limiting and API keys
- [ ] Embedding-based paper similarity for recommendation
- [ ] Dashboard with analytics (most-cited innovation paths, trending operations)
