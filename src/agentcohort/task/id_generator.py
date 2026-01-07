import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path


class TaskIdGenerator:
    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir

    def generate(self) -> str:
        prefix = self._extract_prefix()
        hash_suffix = self._generate_hash()
        return f"{prefix}-{hash_suffix}"

    def _extract_prefix(self) -> str:
        dir_name = self.project_dir.name
        segments = dir_name.replace("-", " ").replace("_", " ").split()
        prefix = "".join(seg[0].lower() for seg in segments if seg) if segments else dir_name[:3].lower()
        return prefix if prefix else "unn"

    def _generate_hash(self) -> str:
        data = f"{os.getpid()}{datetime.now(UTC).isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:4]
