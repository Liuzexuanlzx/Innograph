from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import graph, papers, edges, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    yield


app = FastAPI(
    title="InnoGraph",
    description="Multi-agent innovation genealogy graph API",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(edges.router, prefix="/api/v1/edges", tags=["edges"])
