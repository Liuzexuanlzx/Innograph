from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.task import TaskResult, TaskStatus
from app.models.graph import GraphSnapshot
from app.workers.graph_builder import build_innovation_graph, celery_app

router = APIRouter()


class BuildRequest(BaseModel):
    query: str
    depth: int = Field(default=1, ge=1, le=3)
    max_papers: int = Field(default=30, ge=5, le=100)
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class BuildResponse(BaseModel):
    task_id: str
    status: str = "PENDING"


@router.post("/build", response_model=BuildResponse)
async def build_graph(request: BuildRequest):
    """Dispatch a graph build task."""
    task = build_innovation_graph.delay(
        query=request.query,
        depth=request.depth,
        max_papers=request.max_papers,
        min_confidence=request.min_confidence,
    )
    return BuildResponse(task_id=task.id)


@router.get("/tasks/{task_id}", response_model=TaskResult)
async def get_task_status(task_id: str):
    """Poll task status."""
    result = celery_app.AsyncResult(task_id)

    if result.state == "PENDING":
        return TaskResult(task_id=task_id, status=TaskStatus.PENDING)
    elif result.state == "RUNNING":
        info = result.info or {}
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            progress=info.get("progress", ""),
        )
    elif result.state == "SUCCESS":
        return TaskResult(task_id=task_id, status=TaskStatus.SUCCESS)
    elif result.state == "FAILURE":
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error=str(result.result),
        )
    else:
        return TaskResult(task_id=task_id, status=TaskStatus.RUNNING, progress=result.state)


@router.get("/tasks/{task_id}/snapshot", response_model=GraphSnapshot)
async def get_task_snapshot(task_id: str):
    """Get the graph snapshot for a completed task."""
    result = celery_app.AsyncResult(task_id)

    if result.state != "SUCCESS":
        raise HTTPException(status_code=404, detail=f"Task not complete. Status: {result.state}")

    data = result.result
    if not data:
        raise HTTPException(status_code=404, detail="No result data")

    return GraphSnapshot(**data)
