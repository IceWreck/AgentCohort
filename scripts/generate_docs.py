import os
import subprocess
from pathlib import Path


def generate_help_output(command_args: list[str] | None = None) -> str:
    """Generate help output by running the CLI command with --help."""
    args: list[str] = ["uv", "run", "agentcohort"]
    args.extend(command_args or [])
    args.append("--help")

    env: dict[str, str] = {"CLICOLOR_FORCE": "0", "NO_COLOR": "1"}
    result: subprocess.CompletedProcess[str] = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
        env={**os.environ, **env},
    )

    return result.stdout


def main() -> None:
    """Generate CLI documentation."""
    docs: list[str] = ["# AgentCohort CLI Documentation\n", "This document contains the help text for all CLI commands.\n"]

    commands: list[list[str]] = [
        [],
        ["task"],
        ["task", "create"],
        ["task", "start"],
        ["task", "close"],
        ["task", "reopen"],
        ["task", "status"],
        ["task", "ls"],
        ["task", "ready"],
        ["task", "blocked"],
        ["task", "closed"],
        ["task", "show"],
        ["task", "edit"],
        ["task", "add-note"],
        ["task", "query"],
        ["task", "dep-add"],
        ["task", "dep-remove"],
        ["task", "dep-tree"],
        ["task", "undep"],
        ["task", "link"],
        ["task", "unlink"],
    ]

    for cmd_args in commands:
        if not cmd_args:
            docs.append("## Main Command\n")
        else:
            cmd_name: str = " ".join(cmd_args)
            docs.append(f"## `agentcohort {cmd_name}`\n")

        docs.append("```")
        docs.append(generate_help_output(cmd_args))
        docs.append("```\n")

    output_file: Path = Path(__file__).parent.parent / "docs" / "reference.md"
    output_file.write_text("\n".join(docs))
    print(f"Documentation generated: {output_file}")


if __name__ == "__main__":
    main()
