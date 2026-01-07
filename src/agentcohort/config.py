import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource

from agentcohort.logger import get_logger

logger = get_logger(__name__)


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENTCOHORT_")

    agentcohort_store: Path = Field(default=Path(".agentcohort"))

    @classmethod
    def from_yaml(cls, file_path: Path) -> "Config":
        logger.info(f"loading config file: {file_path}")
        if not file_path.exists():
            logger.error(f"config file not found: {file_path}")
            raise FileNotFoundError(f"config file not found: {file_path}")

        yaml_source = YamlConfigSettingsSource(cls, yaml_file=str(file_path))
        return cls(**yaml_source())

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=4)
