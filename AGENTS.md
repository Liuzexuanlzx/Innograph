# Repository Guidelines

## Project Structure & Module Organization
`backend/` contains the FastAPI app, LangGraph agents, Celery worker code, and pytest suite. Key modules live in `backend/app/agents`, `backend/app/routers`, `backend/app/services`, and `backend/app/models`; tests mirror that structure under `backend/tests`. `frontend/` is a React 19 + Vite client: UI components are in `frontend/src/components`, API wrappers in `frontend/src/api`, shared state in `frontend/src/stores`, hooks in `frontend/src/hooks`, and styling in `frontend/src/styles`. Repo docs live in `docs/`, and operational scripts such as Neo4j schema setup live in `scripts/`.

## Build, Test, and Development Commands
Use Docker for the full stack: `docker compose up -d` starts Neo4j, Redis, backend, Celery, and frontend. For local split-terminal development, use `make dev` for Neo4j + Redis, `make backend-dev`, `make celery-dev`, and `make frontend-dev`. Run backend tests with `cd backend && python -m pytest tests -v`; run backend lint with `cd backend && python -m ruff check app tests`. Build the frontend with `cd frontend && npm run build`. To initialize Neo4j schema from the repo root, run `python scripts/seed_neo4j.py`.

## Coding Style & Naming Conventions
Python targets 3.12, uses 4-space indentation, Ruff with a 100-character line limit, and type hints on service and model boundaries. Frontend code uses TypeScript, 2-space indentation, semicolons, and single quotes. Follow the existing naming split: PascalCase for React components (`GraphCanvas.tsx`), `useX` for hooks, camelCase for utilities, and descriptive test files named `test_<feature>.py`.

## Testing Guidelines
Backend coverage is the current baseline. Keep unit and router tests under `backend/tests/test_agents`, `test_services`, and `test_routers`, and prefer fixtures from `backend/tests/fixtures` for external API payloads. Use `@pytest.mark.asyncio` for async flows and cover both happy-path and fallback behavior. Frontend test and lint targets exist in the `Makefile`, but no first-party frontend test files are checked in yet; add UI tests alongside new interactive logic instead of relying on manual verification alone.

## Commit & Pull Request Guidelines
This workspace snapshot does not include `.git`, so local history cannot be inspected. Use short imperative commit subjects such as `Add graph polling error handling`. PRs should explain user-visible changes, list backend/frontend commands run, link the relevant issue, and include screenshots or short recordings for graph or panel UI updates.

## Security & Configuration Tips
Configuration is loaded from the repo-root `.env` file into both Docker Compose and `backend/app/config.py`. Do not commit real API keys. Treat `frontend/dist`, `frontend/node_modules`, `__pycache__`, and `*.egg-info` as generated artifacts: inspect them when debugging, but do not hand-edit them.
