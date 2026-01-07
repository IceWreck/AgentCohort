from pathlib import Path

import typer

from agentcohort.config import Config
from agentcohort.logger import get_logger, setup_logging

app = typer.Typer()
logger = get_logger(__name__)


@app.command()
def main(
    config_path: str = typer.Option("config/config.yml", help="Path to configuration file"),
) -> None:
    setup_logging()
    logger.info("starting agentcohort")

    config = Config.from_yaml(Path(config_path))
    logger.info(f"loaded configuration: {config.to_json()}")

    logger.info("hello world")


if __name__ == "__main__":
    app()
