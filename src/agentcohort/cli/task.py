import json
import os
import subprocess
from pathlib import Path

import typer

from agentcohort.config import Config
from agentcohort.task.id_generator import TaskIdGenerator
from agentcohort.task.models import TaskStatus, TaskType
from agentcohort.task.repository import MarkdownTaskRepository
from agentcohort.task.services import DependencyService, LinkService, QueryService, TaskService

task_app = typer.Typer(no_args_is_help=True)


def get_services():
    """Initialize and return all required services."""
    config = Config.from_env()
    repo = MarkdownTaskRepository(config.tasks_dir)
    id_gen = TaskIdGenerator(Path.cwd())
    task_service = TaskService(repo, id_gen)
    dep_service = DependencyService(repo)
    link_service = LinkService(repo)
    query_service = QueryService(repo)
    return task_service, dep_service, link_service, query_service, config


@task_app.command()
def create(
    title: str,
    description: str = typer.Option(None, "-d", "--description", help="Task description."),
    design: str = typer.Option(None, "--design", help="Task design."),
    acceptance: str = typer.Option(None, "--acceptance", help="Acceptance criteria."),
    type: TaskType = typer.Option(TaskType.TASK, "-t", "--type", help="Task type."),
    priority: int = typer.Option(2, "-p", "--priority", help="Task priority (0-4, 0=highest)."),
    assignee: str = typer.Option(None, "-a", "--assignee", help="Task assignee."),
    external_ref: str = typer.Option(None, "--external-ref", help="External reference."),
    parent: str = typer.Option(None, "--parent", help="Parent task id."),
) -> None:
    """Create a new task with the specified properties."""
    task_service, _, _, _, _ = get_services()
    task = task_service.create_task(
        title,
        description,
        design,
        acceptance,
        type,
        priority,
        assignee,
        external_ref,
        parent,
    )
    typer.echo(task.id)


@task_app.command()
def start(task_id: str) -> None:
    """Mark a task as in_progress."""
    task_service, _, _, _, _ = get_services()
    task = task_service.start_task(task_id)
    typer.echo(f"Updated {task.id} -> in_progress")


@task_app.command()
def close(task_id: str) -> None:
    """Mark a task as closed."""
    task_service, _, _, _, _ = get_services()
    task = task_service.close_task(task_id)
    typer.echo(f"Updated {task.id} -> closed")


@task_app.command()
def reopen(task_id: str) -> None:
    """Reopen a closed task (sets status back to open)."""
    task_service, _, _, _, _ = get_services()
    task = task_service.reopen_task(task_id)
    typer.echo(f"Updated {task.id} -> open")


@task_app.command()
def status(task_id: str, new_status: TaskStatus) -> None:
    """Set the status of a task to the specified value."""
    task_service, _, _, _, _ = get_services()
    task = task_service.set_status(task_id, new_status)
    typer.echo(f"Updated {task.id} -> {new_status}")


@task_app.command()
def ls(status_filter: TaskStatus = typer.Option(None, "--status", help="Filter by status.")) -> None:
    """List all tasks, optionally filtering by status."""
    task_service, _, _, _, _ = get_services()
    tasks = task_service.list_tasks(status_filter)
    for task in tasks:
        deps_string = f"[{', '.join(task.deps)}]" if task.deps else "[]"
        typer.echo(f"{task.id:8s} [{task.status.value}] - {task.title} <- {deps_string}")


@task_app.command()
def ready() -> None:
    """List tasks that are ready to be started (no blocking dependencies)."""
    task_service, _, _, _, _ = get_services()
    tasks = task_service.get_ready_tasks()
    for task in tasks:
        typer.echo(f"{task.id:8s} [P{task.priority}][{task.status.value}] - {task.title}")


@task_app.command()
def blocked() -> None:
    """List tasks that are blocked by unclosed dependencies."""
    task_service, _, _, _, _ = get_services()
    tasks = task_service.get_blocked_tasks()
    all_tasks = {t.id: t for t in task_service.list_tasks()}
    for task in tasks:
        blockers = [
            dep_id
            for dep_id in task.deps
            if dep_id in all_tasks and all_tasks[dep_id].status != TaskStatus.CLOSED
        ]
        blockers_string = f"[{', '.join(blockers)}]" if blockers else "[]"
        typer.echo(f"{task.id:8s} [P{task.priority}][{task.status.value}] - {task.title} <- {blockers_string}")


@task_app.command()
def closed(limit: int = typer.Option(20, "--limit", help="Number of tasks to show.")) -> None:
    """List recently closed tasks."""
    task_service, _, _, _, _ = get_services()
    tasks = task_service.get_recently_closed_tasks(limit)
    for task in tasks:
        typer.echo(f"{task.id:8s} [{task.status.value}] - {task.title}")


@task_app.command()
def show(task_id: str) -> None:
    """Display detailed information about a task including related tasks."""
    task_service, _, _, _, _ = get_services()
    task = task_service.get_task(task_id)
    all_tasks = {t.id: t for t in task_service.list_tasks()}

    typer.echo("---")
    typer.echo(f"id: {task.id}")
    typer.echo(f"status: {task.status.value}")
    typer.echo(f"deps: {task.deps}")
    typer.echo(f"links: {task.links}")
    typer.echo(f"created: {task.created}")
    typer.echo(f"type: {task.type.value}")
    typer.echo(f"priority: {task.priority}")
    if task.assignee:
        typer.echo(f"assignee: {task.assignee}")
    if task.external_ref:
        typer.echo(f"external-ref: {task.external_ref}")
    if task.parent:
        typer.echo(f"parent: {task.parent}")
    typer.echo("---")
    typer.echo(f"# {task.title}")
    typer.echo("")
    if task.description:
        typer.echo(task.description)
        typer.echo("")
    if task.design:
        typer.echo("## Design")
        typer.echo("")
        typer.echo(task.design)
        typer.echo("")
    if task.acceptance:
        typer.echo("## Acceptance Criteria")
        typer.echo("")
        typer.echo(task.acceptance)
        typer.echo("")
    if task.notes:
        typer.echo("## Notes")
        typer.echo("")
        for note in task.notes:
            typer.echo(f"**{note.timestamp}**")
            typer.echo("")
            typer.echo(note.content)
            typer.echo("")

    blockers = [dep_id for dep_id in task.deps if dep_id in all_tasks and all_tasks[dep_id].status != TaskStatus.CLOSED]
    if blockers:
        typer.echo("## Blockers")
        typer.echo("")
        for blocker_id in blockers:
            blocker = all_tasks[blocker_id]
            typer.echo(f"- {blocker.id} [{blocker.status.value}] {blocker.title}")
        typer.echo("")

    blocking = [t.id for t in all_tasks.values() if task_id in t.deps and t.status != TaskStatus.CLOSED]
    if blocking:
        typer.echo("## Blocking")
        typer.echo("")
        for blocking_id in blocking:
            blocking_task = all_tasks[blocking_id]
            typer.echo(f"- {blocking_task.id} [{blocking_task.status.value}] {blocking_task.title}")
        typer.echo("")

    children = [t.id for t in all_tasks.values() if t.parent == task.id]
    if children:
        typer.echo("## Children")
        typer.echo("")
        for child_id in children:
            child = all_tasks[child_id]
            typer.echo(f"- {child.id} [{child.status.value}] {child.title}")
        typer.echo("")

    if task.links:
        typer.echo("## Linked")
        typer.echo("")
        for link_id in task.links:
            if link_id in all_tasks:
                link = all_tasks[link_id]
                typer.echo(f"- {link.id} [{link.status.value}] {link.title}")
        typer.echo("")


@task_app.command()
def edit(task_id: str) -> None:
    """Open a task's markdown file in your default editor."""
    task_service, _, _, _, config = get_services()
    task = task_service.get_task(task_id)
    file_path = config.tasks_dir / f"{task.id}.md"
    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(file_path)])


@task_app.command()
def add_note(task_id: str, note_text: str | None = typer.Argument(None)) -> None:
    """Add a note to a task."""
    if note_text is None:  # type: ignore[unreachable]
        typer.echo("error: no note provided", err=True)
        raise typer.Exit(1)
    task_service, _, _, _, _ = get_services()
    task = task_service.add_note(task_id, note_text)
    typer.echo(f"Note added to {task.id}")


@task_app.command()
def query(jq_filter: str = typer.Argument(None)) -> None:
    """Query tasks and export as JSON."""
    _, _, _, query_service, _ = get_services()
    tasks = query_service.query_filtered()
    typer.echo(json.dumps([task.model_dump(mode="json") for task in tasks], indent=2))


@task_app.command(name="dep-add")
def dep_add(task_id: str, dep_id: str) -> None:
    """Add a dependency from task_id to dep_id."""
    _, dep_service, _, _, _ = get_services()
    task = dep_service.add_dependency(task_id, dep_id)
    typer.echo(f"Added dependency: {task.id} -> {dep_id}")


@task_app.command(name="dep-remove")
def dep_remove(task_id: str, dep_id: str) -> None:
    """Remove a dependency from task_id to dep_id."""
    _, dep_service, _, _, _ = get_services()
    task = dep_service.remove_dependency(task_id, dep_id)
    typer.echo(f"Removed dependency: {task.id} -/-> {dep_id}")


@task_app.command(name="dep-tree")
def dep_tree(task_id: str, full: bool = typer.Option(False, "--full", help="Show all occurrences.")) -> None:
    """Display the dependency tree for a task."""
    _, dep_service, _, _, _ = get_services()
    tree_str = dep_service.get_dependency_tree(task_id, full)
    typer.echo(tree_str)


@task_app.command(name="undep")
def undep(task_id: str, dep_id: str) -> None:
    """Remove a dependency from task_id to dep_id (alias for dep-remove)."""
    _, dep_service, _, _, _ = get_services()
    task = dep_service.remove_dependency(task_id, dep_id)
    typer.echo(f"Removed dependency: {task.id} -/-> {dep_id}")


@task_app.command()
def link(task_ids: list[str] = typer.Argument(...)) -> None:
    """Create bidirectional links between multiple tasks."""
    _, _, link_service, _, _ = get_services()
    count = link_service.link_tasks(task_ids)
    typer.echo(f"Added {count} link(s) between {len(task_ids)} tasks")


@task_app.command()
def unlink(task_id: str, target_id: str) -> None:
    """Remove a link between two tasks."""
    _, _, link_service, _, _ = get_services()
    link_service.unlink_tasks(task_id, target_id)
    typer.echo(f"Removed link: {task_id} <-> {target_id}")
