import typer

from agentcohort.task_cli import task_app

app = typer.Typer()
app.add_typer(task_app, name="task", help="task tracking and management")


def main() -> None:
    app()


if __name__ == "__main__":
    app()
