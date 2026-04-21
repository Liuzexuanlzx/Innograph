.PHONY: dev up down seed test lint

up:
	docker compose up -d

down:
	docker compose down

dev:
	docker compose up neo4j redis -d
	@echo "Neo4j: http://localhost:7474  Redis: localhost:6379"

seed:
	cd backend && python -m scripts.seed_neo4j

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

celery-dev:
	cd backend && celery -A app.workers.graph_builder worker --loglevel=info

frontend-dev:
	cd frontend && npm run dev

test-backend:
	cd backend && python -m pytest tests/ -v

test-frontend:
	cd frontend && npx vitest --run

test: test-backend test-frontend

lint-backend:
	cd backend && python -m ruff check app/ tests/

lint-frontend:
	cd frontend && npx eslint src/
