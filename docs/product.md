# InnoGraph — Product Overview

## What is InnoGraph?

InnoGraph is a multi-agent innovation genealogy graph for scientific literature. Given a seed paper (DOI, title, or arXiv ID), it builds an explainable directed graph where each edge describes **how** one paper improves upon another, using a structured 3-level taxonomy with evidence spans and confidence scores.

## Problem

Existing tools like Connected Papers and Semantic Scholar show citation networks — who cites whom — but never explain **what changed** between two papers. Researchers still have to read dozens of abstracts to understand the lineage of an idea.

## How InnoGraph is Different

| Feature | Connected Papers | Semantic Scholar | InnoGraph |
|---|---|---|---|
| Citation graph | ✓ | ✓ | ✓ |
| Explains **how** B improves A | ✗ | ✗ | ✓ |
| Structured edge taxonomy | ✗ | ✗ | ✓ (3 levels) |
| Evidence spans with confidence | ✗ | ✗ | ✓ |
| Lineage narratives | ✗ | ✗ | ✓ |
| Human-in-the-loop correction | ✗ | ✗ | ✓ |

## Core Concepts

### 3-Level Edge Taxonomy

Every innovation edge is classified along three levels:

**L1 — Relation Type** (9 values): The high-level relationship between two papers.

`IMPROVES_ON` · `EXTENDS` · `COMBINES_WITH` · `APPLIES_TO` · `SIMPLIFIES` · `GENERALIZES` · `PROVIDES_THEORY_FOR` · `REPRODUCES` · `CONTRADICTS`

**L2 — Innovation Dimension** (14 values): What aspect of the work changed.

`ACCURACY` · `EFFICIENCY` · `SCALABILITY` · `ROBUSTNESS` · `GENERALIZATION` · `INTERPRETABILITY` · `DATA_EFFICIENCY` · `SIMPLICITY` · `NOVELTY` · `COVERAGE` · `FAIRNESS` · `SAFETY` · `COST` · `USABILITY`

**L3 — Operation** (15 values): The specific technical change.

`ADDS_MODULE` · `REPLACES_BACKBONE` · `CHANGES_LOSS_FUNCTION` · `MODIFIES_ARCHITECTURE` · `INTRODUCES_PRETRAINING` · `ADDS_DATA_AUGMENTATION` · `CHANGES_OPTIMIZATION` · `ADDS_REGULARIZATION` · `INTRODUCES_NEW_TASK` · `CHANGES_REPRESENTATION` · `SCALES_UP` · `ADDS_FEEDBACK_LOOP` · `INTRODUCES_BENCHMARK` · `PROVIDES_PROOF` · `COMBINES_MODALITIES`

### Evidence & Confidence

Each edge carries:
- **Evidence spans** — exact text excerpts from the papers that support the classification, with section labels and relevance scores.
- **Confidence score** (0–1) — assigned by a verifier agent. Edges below 0.5 are marked `UNSUPPORTED`.
- **Verdict** — `SUPPORTED`, `WEAK`, or `UNSUPPORTED`.

### PaperCard

An LLM-extracted structured summary for each paper: problem statement, method summary, key modules, claimed gains, limitations, datasets, and baselines.

## Feature List

- Seed paper resolution from DOI, title, or arXiv ID
- Automatic retrieval of references, citations, and recommendations
- LLM-powered structured extraction (PaperCards + InnovationEdges)
- Multi-agent verification with confidence scoring
- Lineage narrative generation
- Interactive graph visualization (nodes by year/citations, edges by relation type/confidence)
- Human-in-the-loop edge correction via PATCH API
- Paper search via OpenAlex
- Async task processing with real-time polling
- Redis caching (24h API responses, 7d LLM extractions)
- Neo4j persistence

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic |
| Agent orchestration | LangGraph (LangChain) |
| LLM | OpenAI GPT-4o (primary), Anthropic Claude (fallback) |
| Task queue | Celery + Redis |
| Graph database | Neo4j 5 |
| Cache | Redis 7 |
| Frontend | React 19, TypeScript, Vite |
| State management | Zustand |
| Graph visualization | Cytoscape.js |
| Academic APIs | OpenAlex, Semantic Scholar |
| Infrastructure | Docker Compose |
