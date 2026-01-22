import subprocess
from pathlib import Path

from agentcohort.worktree.exceptions import (
    BranchExistsError,
    BranchNotFoundError,
    GitCommandError,
    NotInGitRepoError,
)
from agentcohort.worktree.models import WorktreeInfo


class GitClient:
    """Client for executing git operations."""

    def __init__(self, repo_path: Path | None = None):
        """Initialize GitClient with a repository path.

        Args:
            repo_path: Path to the git repository. Defaults to current working directory.
        """
        self.repo_path = str(repo_path or Path.cwd())

    def _run(self, *args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
        """Run a git command with -C flag for repo path.

        Args:
            args: Git command arguments
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess instance

        Raises:
            GitCommandError: If the git command fails
        """
        try:
            return subprocess.run(
                ["git", "-C", self.repo_path, *args],
                check=True,
                capture_output=capture_output,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise GitCommandError(f"Git command failed: {e.stderr if capture_output else str(e)}") from e

    def is_git_repo(self) -> bool:
        """Check if the current directory is a git repository.

        Returns:
            True if in a git repository, False otherwise
        """
        try:
            self._run("rev-parse", "--git-dir", capture_output=True)
            return True
        except GitCommandError:
            return False

    def get_repo_root(self) -> Path:
        """Get the root path of the git repository.

        Returns:
            Path to the repository root

        Raises:
            NotInGitRepoError: If not in a git repository
        """
        if not self.is_git_repo():
            raise NotInGitRepoError("Not in a git repository")

        result = self._run("rev-parse", "--show-toplevel", capture_output=True)
        return Path(result.stdout.strip())

    def get_repo_name(self) -> str:
        """Get the name of the git repository.

        Returns:
            Repository name (directory name of the repo root)

        Raises:
            NotInGitRepoError: If not in a git repository
        """
        repo_root = self.get_repo_root()
        return repo_root.name.lower()

    @property
    def current_branch(self) -> str:
        """Get the name of the current branch.

        Returns:
            Current branch name

        Raises:
            NotInGitRepoError: If not in a git repository
            GitCommandError: If unable to determine current branch
        """
        if not self.is_git_repo():
            raise NotInGitRepoError("Not in a git repository")

        result = self._run("rev-parse", "--abbrev-ref", "HEAD", capture_output=True)
        return result.stdout.strip()

    def branch_exists(self, branch: str) -> bool:
        """Check if a branch exists locally.

        Args:
            branch: Branch name to check

        Returns:
            True if the branch exists, False otherwise
        """
        try:
            self._run("show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
            return True
        except GitCommandError:
            return False

    def worktree_add(
        self,
        path: Path,
        branch: str,
        new_branch: bool = False,
        base: str | None = None,
    ) -> None:
        """Add a new worktree.

        Args:
            path: Path where the worktree will be created
            branch: Branch name for the worktree
            new_branch: Whether to create a new branch
            base: Base branch to create from (only used when new_branch=True)

        Raises:
            GitCommandError: If the worktree creation fails
            BranchExistsError: If creating a new branch that already exists
            BranchNotFoundError: If using existing branch that doesn't exist
        """
        if new_branch:
            if self.branch_exists(branch):
                raise BranchExistsError(f"Branch '{branch}' already exists")
            cmd = ["worktree", "add", "-b", branch, str(path)]
            if base:
                cmd.append(base)
        else:
            if not self.branch_exists(branch):
                raise BranchNotFoundError(f"Branch '{branch}' not found")
            cmd = ["worktree", "add", str(path), branch]

        self._run(*cmd)

    def worktree_list(self) -> list[WorktreeInfo]:
        """List all worktrees in the repository.

        Returns:
            List of WorktreeInfo objects (is_main defaults to False)

        Raises:
            NotInGitRepoError: If not in a git repository
        """
        if not self.is_git_repo():
            raise NotInGitRepoError("Not in a git repository")

        result = self._run("worktree", "list", "--porcelain", capture_output=True)
        worktrees: list[WorktreeInfo] = []
        current_worktree: dict[str, str | None] = {}

        for line in result.stdout.strip().split("\n"):
            if not line:
                if current_worktree and "path" in current_worktree and "head" in current_worktree:
                    # Ensure we have all required fields before appending
                    path_str = current_worktree["path"]
                    head_str = current_worktree["head"]
                    if path_str is not None and head_str is not None:
                        worktrees.append(
                            WorktreeInfo(
                                path=Path(path_str),
                                head=head_str,
                                branch=current_worktree.get("branch"),
                            )
                        )
                    current_worktree = {}
                continue

            if line.startswith("worktree "):
                current_worktree["path"] = line.split(" ", 1)[1]
            elif line.startswith("HEAD "):
                current_worktree["head"] = line.split(" ", 1)[1]
            elif line.startswith("branch "):
                current_worktree["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
            elif line == "detached":
                current_worktree["branch"] = None

        if current_worktree and "path" in current_worktree and "head" in current_worktree:
            path_str = current_worktree["path"]
            head_str = current_worktree["head"]
            if path_str is not None and head_str is not None:
                worktrees.append(
                    WorktreeInfo(
                        path=Path(path_str),
                        head=head_str,
                        branch=current_worktree.get("branch"),
                    )
                )

        return worktrees

    def worktree_remove(self, path: Path, force: bool = False) -> None:
        """Remove a worktree.

        Args:
            path: Path to the worktree to remove
            force: Whether to force removal even if worktree has changes

        Raises:
            GitCommandError: If the worktree removal fails
        """
        cmd = ["worktree", "remove", str(path)]
        if force:
            cmd.append("--force")

        self._run(*cmd)
