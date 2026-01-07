import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from agentcohort.logger import get_logger

logger = get_logger(__name__)


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENTCOHORT_")

    agentcohort_store: Path = Field(default=Path(".agentcohort"))
    tasks_dir: Path = Field(default=Path(".agentcohort/tasks"))

    @classmethod
    def from_env(cls) -> "Config":
        logger.info("loading config from environment")
        return cls()

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=4)
