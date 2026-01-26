import contextlib
import subprocess
from pathlib import Path

from agentcohort.config import Config
from agentcohort.worktree.exceptions import WorktreeNotFoundError
from agentcohort.worktree.git import GitClient
from agentcohort.worktree.models import WorktreeCreateResult, WorktreeInfo


class WorktreeService:
    """Service for managing git worktrees."""

    def __init__(self, git_client: GitClient, config: Config):
        """Initialize WorktreeService with a GitClient and Config.

        Args:
            git_client: GitClient instance for executing git operations
            config: Config instance for accessing configuration
        """
        self.git = git_client
        self.config = config

    def create_worktree(
        self,
        name: str,
        branch: str | None = None,
        base: str | None = None,
        existing: bool = False,
        path: Path | None = None,
        post_setup: str | None = None,
    ) -> WorktreeCreateResult:
        """Create a new worktree.

        Args:
            name: Name for the worktree
            branch: Branch name (defaults to name)
            base: Base branch to create from (defaults to current branch)
            existing: Use existing branch instead of creating new one
            path: Custom worktree path (defaults to ../<repo-name>-<name>)
            post_setup: Command to run after creation

        Returns:
            WorktreeCreateResult with creation details

        Raises:
            NotInGitRepoError: If not in a git repository
            BranchExistsError: If creating a new branch that already exists
            BranchNotFoundError: If using existing branch that doesn't exist
            GitCommandError: If git operations fail
        """
        # Determine branch name
        if branch is None:
            branch = name

        # Determine worktree path
        if path is None:
            repo_root = self.git.repo_root
            repo_name = self.git.repo_name
            path = repo_root.parent / f"{repo_name}-{name}"
        else:
            path = path.resolve()

        # Determine base branch (only used when creating new branch)
        if base is None and not existing:
            base = self.git.default_branch

        # Create the worktree
        self.git.worktree_add(
            path=path,
            branch=branch,
            new_branch=not existing,
            base=base if not existing else None,
        )

        # Symlink agentcohort_store from main repo if it exists
        self._symlink_agentcohort_store(path)

        # Run post-setup command if provided
        post_setup_output = None
        if post_setup:
            post_setup_output = self.run_post_setup(path, post_setup)

        return WorktreeCreateResult(
            worktree_path=path,
            branch=branch,
            created_new_branch=not existing,
            post_setup_output=post_setup_output,
        )

    def _symlink_agentcohort_store(self, worktree_path: Path) -> None:
        """Symlink the main repo's agentcohort_store into the worktree.

        Args:
            worktree_path: Path to the newly created worktree
        """
        store_name = self.config.agentcohort_store.name

        worktrees = self.git.worktree_list()
        if not worktrees:
            return

        main_repo_path = worktrees[0].path
        main_store_path = main_repo_path / store_name
        new_store_path = worktree_path / store_name

        if main_store_path.exists() and not new_store_path.exists():
            with contextlib.suppress(OSError):
                new_store_path.symlink_to(main_store_path)

    def list_worktrees(self) -> list[WorktreeInfo]:
        """List all worktrees in the repository.

        Returns:
            List of WorktreeInfo objects with is_main set correctly

        Raises:
            NotInGitRepoError: If not in a git repository
        """
        worktrees = self.git.worktree_list()

        # Mark the first worktree as main
        if worktrees:
            worktrees[0] = worktrees[0].model_copy(update={"is_main": True})

        return worktrees

    def remove_worktree(self, name: str, force: bool = False) -> Path:
        """Remove a worktree by name or path.

        Args:
            name: Name of the worktree (original name without prefix) or full path
            force: Whether to force removal even if worktree has changes

        Returns:
            Path of the removed worktree

        Raises:
            WorktreeNotFoundError: If the worktree doesn't exist
            GitCommandError: If git operations fail
        """
        # Check if name is a full path
        potential_path = Path(name).resolve()
        worktrees = self.list_worktrees()
        target_path = None

        # First try to match by exact path
        for wt in worktrees:
            if wt.path.resolve() == potential_path:
                target_path = wt.path
                break

        # If not found, try to match by directory name (exact match)
        if target_path is None:
            for wt in worktrees:
                if wt.path.name == name:
                    target_path = wt.path
                    break

        # If still not found, try with repo prefix applied
        if target_path is None:
            repo_name = self.git.repo_name
            prefixed_name = f"{repo_name}-{name}"
            for wt in worktrees:
                if wt.path.name == prefixed_name:
                    target_path = wt.path
                    break

        if target_path is None:
            raise WorktreeNotFoundError(f"Worktree '{name}' not found")

        # Remove the worktree
        self.git.worktree_remove(target_path, force=force)
        return target_path

    def run_post_setup(self, worktree_path: Path, command: str) -> str:
        """Execute a post-setup command in the worktree directory.

        Args:
            worktree_path: Path to the worktree
            command: Command to execute

        Returns:
            Combined stdout and stderr output

        Raises:
            GitCommandError: If the command fails
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5-minute timeout
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n"
                output += result.stderr

            if result.returncode != 0:
                output = f"Warning: Post-setup command exited with code {result.returncode}\n{output}"

            return output

        except subprocess.TimeoutExpired:
            return "Warning: Post-setup command timed out after 5 minutes"
        except Exception as e:
            return f"Warning: Post-setup command failed: {str(e)}"
