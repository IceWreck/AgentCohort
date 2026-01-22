import typer

from agentcohort.cli.task import task_app
from agentcohort.cli.worktree import worktree_app

app = typer.Typer(no_args_is_help=True, help="AgentCohort - Agent Task Tracking & Orchestration Tool.")
app.add_typer(task_app, name="task", help="Task tracking and management.")
app.add_typer(worktree_app, name="worktree", help="Git worktree management.")


def main() -> None:
    app()


if __name__ == "__main__":
    app()
