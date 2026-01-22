class WorktreeError(Exception):
    """Base exception for worktree operations."""

    pass


class NotInGitRepoError(WorktreeError):
    """Raised when not in a git repository."""

    pass


class WorktreeExistsError(WorktreeError):
    """Raised when a worktree already exists at the specified path."""

    pass


class WorktreeNotFoundError(WorktreeError):
    """Raised when a worktree doesn't exist at the specified path."""

    pass


class BranchExistsError(WorktreeError):
    """Raised when attempting to create a branch that already exists."""

    pass


class BranchNotFoundError(WorktreeError):
    """Raised when a branch doesn't exist when using --existing."""

    pass


class GitCommandError(WorktreeError):
    """Raised when a git command execution fails."""

    pass
