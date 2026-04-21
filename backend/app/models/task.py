from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    progress: str = ""
    error: str | None = None
