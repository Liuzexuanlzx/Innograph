# InnoGraph — Demo & Usage

## Prerequisites

Start the infrastructure and services:

```bash
# Start Neo4j + Redis
make dev

# Initialize Neo4j schema (first time only)
make seed

# Start backend + worker (separate terminals)
make backend-dev
make celery-dev

# Start frontend
make frontend-dev
```

Or run everything via Docker:

```bash
make up
```

## API Usage

### 1. Build a Graph

Submit a seed paper query to start the multi-agent pipeline:

```bash
curl -X POST http://localhost:8000/api/v1/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Attention Is All You Need",
    "depth": 1,
    "max_papers": 30,
    "min_confidence": 0.5
  }'
```

Response:

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PENDING"
}
```

**Parameters:**

| Field | Type | Default | Description |
|---|---|---|---|
| `query` | string | required | DOI, arXiv ID, or paper title |
| `depth` | int | 1 | Expansion depth (1–3) |
| `max_papers` | int | 30 | Maximum papers to retrieve (5–100) |
| `min_confidence` | float | 0.5 | Minimum confidence threshold (0.0–1.0) |

### 2. Poll Task Status

Poll until `status` is `SUCCESS`:

```bash
curl http://localhost:8000/api/v1/graph/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Response (while running):

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "RUNNING",
  "progress": "relation_extractor",
  "error": null
}
```

Response (complete):

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "progress": "",
  "error": null
}
```

### 3. Fetch the Graph Snapshot

Once the task succeeds, retrieve the full graph:

```bash
curl http://localhost:8000/api/v1/graph/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890/snapshot
```

### 4. Search Papers

```bash
curl "http://localhost:8000/api/v1/papers/search?q=transformer+architecture"
```

### 5. Inspect an Edge

```bash
curl http://localhost:8000/api/v1/edges/edge-uuid-here
```

### 6. Correct an Edge (Human-in-the-Loop)

```bash
curl -X PATCH http://localhost:8000/api/v1/edges/edge-uuid-here \
  -H "Content-Type: application/json" \
  -d '{
    "relation_type": "EXTENDS",
    "confidence": 0.9,
    "verdict": "SUPPORTED"
  }'
```

## Sample GraphSnapshot Output

Below is a truncated example of what the snapshot endpoint returns:

```json
{
  "seed_paper_id": "W2741809807",
  "papers": [
    {
      "openalex_id": "W2741809807",
      "doi": "10.48550/arXiv.1706.03762",
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      "publication_year": 2017,
      "venue": "NeurIPS",
      "citation_count": 120000,
      "fields_of_study": ["Computer Science"]
    },
    {
      "openalex_id": "W2963403868",
      "doi": "10.48550/arXiv.1810.04805",
      "title": "BERT: Pre-training of Deep Bidirectional Transformers",
      "authors": ["Jacob Devlin", "Ming-Wei Chang"],
      "publication_year": 2018,
      "venue": "NAACL",
      "citation_count": 95000,
      "fields_of_study": ["Computer Science"]
    }
  ],
  "paper_cards": [
    {
      "paper_id": "W2963403868",
      "problem": "Existing language models are unidirectional, limiting pre-training effectiveness",
      "method_summary": "Masked language modeling with bidirectional Transformer encoder",
      "key_modules": ["Masked LM objective", "Next sentence prediction", "WordPiece tokenizer"],
      "claimed_gains": ["SOTA on 11 NLP tasks", "+7.7% GLUE absolute improvement"],
      "limitations": ["Discrepancy between pre-training and fine-tuning due to [MASK] token"],
      "datasets": ["BooksCorpus", "English Wikipedia"],
      "baselines": ["GPT", "ELMo"]
    }
  ],
  "innovation_edges": [
    {
      "id": "e-001",
      "source_paper_id": "W2741809807",
      "target_paper_id": "W2963403868",
      "relation_type": "EXTENDS",
      "innovation_dimensions": ["ACCURACY", "GENERALIZATION"],
      "operations": ["INTRODUCES_PRETRAINING", "MODIFIES_ARCHITECTURE"],
      "confidence": 0.92,
      "verdict": "SUPPORTED",
      "evidence": [
        {
          "paper_id": "W2963403868",
          "text": "Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
          "section": "abstract",
          "score": 0.95
        }
      ],
      "summary": "BERT extends the Transformer architecture by introducing bidirectional pre-training via masked language modeling, achieving broad improvements across NLP benchmarks."
    }
  ],
  "summaries": {
    "lineage": "The Transformer architecture introduced self-attention as a replacement for recurrence. BERT extended this by adding bidirectional pre-training..."
  }
}
```

## Frontend

Open `http://localhost:5173` in your browser. Enter a paper title or DOI in the search bar and click Build. The graph will render once the pipeline completes, with:

- Nodes colored by publication year, sized by citation count
- Edges colored by L1 relation type, opacity scaled by confidence
- Click any node to view its PaperCard
- Click any edge to see the full taxonomy classification and evidence spans
