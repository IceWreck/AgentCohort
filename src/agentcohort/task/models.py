from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class TaskType(StrEnum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    EPIC = "epic"
    CHORE = "chore"


class Note(BaseModel):
    timestamp: str
    content: str


class TaskBase(BaseModel):
    id: str
    status: TaskStatus
    type: TaskType
    created: str
    priority: int = Field(default=2, ge=0, le=4)
    deps: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    assignee: str | None = None
    external_ref: str | None = None
    parent: str | None = None
    description: str | None = None
    design: str | None = None
    acceptance: str | None = None

    @field_validator("created", mode="before")
    @classmethod
    def validate_created(cls, v: str | datetime) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class TaskFrontmatter(TaskBase):
    pass


class Task(TaskBase):
    title: str
    notes: list[Note] = Field(default_factory=list)
