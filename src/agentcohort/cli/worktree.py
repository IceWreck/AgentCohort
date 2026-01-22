from pathlib import Path

import typer

from agentcohort.worktree.exceptions import WorktreeError
from agentcohort.worktree.git import GitClient
from agentcohort.worktree.services import WorktreeService

worktree_app = typer.Typer(no_args_is_help=True)


def get_service() -> WorktreeService:
    """Initialize and return WorktreeService with GitClient."""
    git_client = GitClient()
    return WorktreeService(git_client)


@worktree_app.command()
def create(
    name: str,
    branch: str = typer.Option(None, "-b", "--branch", help="Branch name (defaults to <name>)."),
    base: str = typer.Option(None, "--base", help="Base branch to create from (defaults to current branch)."),
    existing: bool = typer.Option(False, "--existing", help="Use existing branch instead of creating new one."),
    path: str = typer.Option(None, "--path", help="Custom worktree path (defaults to ../<repo-name>-<name>)."),
    post_setup: str = typer.Option(None, "--post-setup", help='Command to run after creation (e.g., "uv sync").'),
) -> None:
    """Create a new worktree."""
    try:
        service = get_service()
        result = service.create_worktree(
            name=name,
            branch=branch,
            base=base,
            existing=existing,
            path=Path(path) if path else None,
            post_setup=post_setup,
        )

        typer.echo(f"Created worktree at: {result.worktree_path}")
        typer.echo(f"Branch: {result.branch}")
        if result.created_new_branch:
            typer.echo("  (new branch created)")
        else:
            typer.echo("  (using existing branch)")

        if result.post_setup_output:
            typer.echo("\nPost-setup command output:")
            typer.echo(result.post_setup_output)

    except WorktreeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@worktree_app.command()
def ls() -> None:
    """List all worktrees."""
    try:
        service = get_service()
        worktrees = service.list_worktrees()

        if not worktrees:
            typer.echo("No worktrees found.")
            return

        for wt in worktrees:
            main_marker = " (main)" if wt.is_main else ""
            typer.echo(f"{wt.path}{main_marker}")
            branch_display = wt.branch if wt.branch else "(detached)"
            typer.echo(f"  Branch: {branch_display}")
            typer.echo(f"  HEAD: {wt.head[:8]}")

    except WorktreeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@worktree_app.command()
def remove(
    name: str,
    force: bool = typer.Option(False, "--force", help="Force removal even if worktree has changes."),
) -> None:
    """Remove a worktree."""
    try:
        service = get_service()
        removed_path = service.remove_worktree(name, force=force)
        typer.echo(f"Removed worktree: {removed_path}")

    except WorktreeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
