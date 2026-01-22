from pathlib import Path

from pydantic import BaseModel


class WorktreeInfo(BaseModel):
    """Represents information about a git worktree."""

    path: Path
    branch: str | None
    head: str
    is_main: bool = False


class WorktreeCreateResult(BaseModel):
    """Result of a worktree creation operation."""

    worktree_path: Path
    branch: str
    created_new_branch: bool
    post_setup_output: str | None = None
