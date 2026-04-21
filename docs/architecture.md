# InnoGraph — Architecture

## System Topology

```mermaid
graph TB
    User([User / Browser])

    subgraph Frontend
        Vite[Vite Dev Server :5173]
        React[React 19 + Zustand]
        Cytoscape[Cytoscape.js]
    end

    subgraph Backend
        FastAPI[FastAPI :8000]
        Celery[Celery Worker]
        LangGraph[LangGraph Workflow]
    end

    subgraph Data
        Neo4j[(Neo4j :7687)]
        Redis[(Redis :6379)]
    end

    subgraph External
        OpenAlex[OpenAlex API]
        S2[Semantic Scholar API]
        OpenAI[OpenAI GPT-4o]
        Anthropic[Anthropic Claude]
    end

    User --> Vite
    Vite -->|/api proxy| FastAPI
    React --> Cytoscape

    FastAPI -->|dispatch task| Redis
    FastAPI -->|poll result| Redis
    Celery -->|consume task| Redis
    Celery --> LangGraph

    LangGraph --> OpenAlex
    LangGraph --> S2
    LangGraph --> OpenAI
    LangGraph --> Anthropic
    LangGraph --> Neo4j
    LangGraph -->|cache| Redis

    FastAPI -->|read snapshot| Redis
    FastAPI -->|query edges| Neo4j
```

## LangGraph Workflow Pipeline

```mermaid
graph LR
    SP[seed_planner] --> RT[retrieval]
    RT --> PR[paper_reader]
    PR --> RE[relation_extractor]
    RE --> VF[verifier]
    VF -->|rejected_pairs & iteration < max| RE
    VF -->|continue| GS[graph_summarizer]
    GS --> PG[persist_graph]
    PG --> END([END])
```

| Node | Responsibility |
|---|---|
| **seed_planner** | Resolves user query (DOI/title/arXiv ID) to an OpenAlex work ID |
| **retrieval** | Fetches references + citations (OpenAlex) and recommendations (Semantic Scholar), deduplicates by title |
| **paper_reader** | LLM extracts structured PaperCards from abstracts (batches of 5) |
| **relation_extractor** | LLM classifies innovation edges using the 3-level taxonomy (batches of 5) |
| **verifier** | LLM assigns confidence scores; filters edges < 0.5 as UNSUPPORTED (batches of 5) |
| **graph_summarizer** | LLM generates lineage narratives for the graph |
| **persist_graph** | Writes papers, paper cards, and verified edges to Neo4j |

State fields annotated with `_add_list` (`raw_papers`, `paper_cards`, `candidate_edges`, `verified_edges`, `errors`) accumulate across nodes rather than overwrite.

## Frontend ↔ Backend Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as FastAPI
    participant Q as Celery + Redis
    participant WF as LangGraph Workflow
    participant DB as Neo4j

    U->>FE: Enter seed paper query
    FE->>API: POST /api/v1/graph/build
    API->>Q: Dispatch build_innovation_graph task
    API-->>FE: { task_id, status: "PENDING" }

    loop Every 2 seconds
        FE->>API: GET /api/v1/graph/tasks/{task_id}
        API->>Q: Check AsyncResult
        API-->>FE: { status: "RUNNING", progress }
    end

    Q->>WF: Execute workflow
    WF->>DB: persist_graph
    WF-->>Q: Result stored

    FE->>API: GET /api/v1/graph/tasks/{task_id}
    API-->>FE: { status: "SUCCESS" }
    FE->>API: GET /api/v1/graph/tasks/{task_id}/snapshot
    API-->>FE: GraphSnapshot (papers, cards, edges, summaries)
    FE->>U: Render interactive graph
```

## Data Model

```mermaid
erDiagram
    Paper {
        string openalex_id PK
        string doi
        string s2_id
        string title
        string abstract
        string[] authors
        int publication_year
        string venue
        int citation_count
        int reference_count
        string[] fields_of_study
        string url
    }

    PaperCard {
        string paper_id FK
        string problem
        string method_summary
        string[] key_modules
        string[] claimed_gains
        string[] limitations
        string[] datasets
        string[] baselines
    }

    InnovationEdge {
        string id PK
        string source_paper_id FK
        string target_paper_id FK
        RelationType relation_type
        InnovationDimension[] innovation_dimensions
        Operation[] operations
        float confidence
        Verdict verdict
        string summary
    }

    EvidenceSpan {
        string paper_id FK
        string text
        string section
        float score
    }

    GraphSnapshot {
        string seed_paper_id FK
        dict summaries
    }

    Paper ||--o| PaperCard : "has card"
    Paper ||--o{ InnovationEdge : "source"
    Paper ||--o{ InnovationEdge : "target"
    InnovationEdge ||--o{ EvidenceSpan : "supported by"
    GraphSnapshot ||--o{ Paper : "contains"
    GraphSnapshot ||--o{ PaperCard : "contains"
    GraphSnapshot ||--o{ InnovationEdge : "contains"
```

## Docker Service Topology

```mermaid
graph TB
    subgraph Docker Compose
        neo4j["neo4j:5<br/>:7474 (HTTP) / :7687 (Bolt)"]
        redis["redis:7-alpine<br/>:6379"]
        backend["backend (FastAPI)<br/>:8000<br/>uvicorn app.main:app"]
        celery["celery_worker<br/>concurrency=2<br/>same image as backend"]
        frontend["frontend (Vite)<br/>:5173<br/>npm run dev"]
    end

    neo4j --- backend
    neo4j --- celery
    redis --- backend
    redis --- celery
    backend --- frontend

    backend -->|depends_on healthy| neo4j
    backend -->|depends_on healthy| redis
    celery -->|depends_on healthy| neo4j
    celery -->|depends_on healthy| redis
    frontend -->|depends_on| backend
```

| Service | Image | Ports | Notes |
|---|---|---|---|
| neo4j | `neo4j:5` | 7474, 7687 | APOC plugin enabled, auth: `neo4j/innograph_dev` |
| redis | `redis:7-alpine` | 6379 | Health check via `redis-cli ping` |
| backend | `./backend` | 8000 | FastAPI with hot reload, reads `.env` |
| celery_worker | `./backend` | — | Same image, different CMD (`celery -A ...`) |
| frontend | `./frontend` | 5173 | Vite dev server, proxies `/api` to backend |

Volumes: `neo4j_data`, `neo4j_logs` for persistence.
