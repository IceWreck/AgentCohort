import json
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from agentcohort.task.exceptions import TaskNotFoundError
from agentcohort.task.models import Note, Task, TaskMetadata, TaskStatus
from agentcohort.task.utils import PartialIdMatcher


class TaskRepository(ABC):
    @abstractmethod
    def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    def get(self, task_id: str) -> Task:
        pass

    @abstractmethod
    def find_by_partial_id(self, partial_id: str) -> Task:
        pass

    @abstractmethod
    def list_all(self) -> list[Task]:
        pass

    @abstractmethod
    def find_by_status(self, status: TaskStatus) -> list[Task]:
        pass

    @abstractmethod
    def find_ready(self) -> list[Task]:
        pass

    @abstractmethod
    def find_blocked(self) -> list[Task]:
        pass

    @abstractmethod
    def find_recently_closed(self, limit: int = 20) -> list[Task]:
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    def delete(self, task_id: str) -> None:
        pass

    @abstractmethod
    def get_all_ids(self) -> list[str]:
        pass

    @abstractmethod
    def add_note_to_task(self, task_id: str, note_content: str) -> Task:
        pass


class DirectoryTaskRepository(TaskRepository):
    def __init__(self, tasks_dir: Path) -> None:
        self.tasks_dir = tasks_dir
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def _get_task_dir(self, task_id: str) -> Path:
        return self.tasks_dir / task_id

    def _get_all_task_dirs(self) -> list[Path]:
        return [d for d in self.tasks_dir.iterdir() if d.is_dir()]

    def _get_metadata_path(self, task_dir: Path) -> Path:
        return task_dir / "metadata.json"

    def _read_metadata(self, task_dir: Path) -> TaskMetadata:
        metadata_path = self._get_metadata_path(task_dir)
        if not metadata_path.exists():
            raise TaskNotFoundError(f"task metadata not found in {task_dir}")
        data = json.loads(metadata_path.read_text())
        return TaskMetadata.model_validate(data)

    def _write_metadata(self, task_dir: Path, metadata: TaskMetadata) -> None:
        metadata_path = self._get_metadata_path(task_dir)
        metadata_path.write_text(json.dumps(metadata.model_dump(mode="json"), indent=2))

    def _read_markdown_file(self, task_dir: Path, filename: str) -> str:
        file_path = task_dir / filename
        if file_path.exists():
            return file_path.read_text()
        return ""

    def _write_markdown_file(self, task_dir: Path, filename: str, content: str) -> None:
        file_path = task_dir / filename
        task_dir.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def _read_all_notes(self, task_dir: Path) -> list[Note]:
        notes: list[Note] = []
        for file_path in sorted(task_dir.glob("note-*.md")):
            note = self._read_note_file(file_path)
            if note:
                notes.append(note)
        return notes

    def _read_note_file(self, file_path: Path) -> Note | None:
        filename = file_path.name
        if not filename.startswith("note-") or not filename.endswith(".md"):
            return None
        timestamp_str = filename[5:-3]
        try:
            dt = datetime.strptime(timestamp_str, "%Y%m%dT%H%M%S%f")
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
        content = file_path.read_text()
        return Note(timestamp=formatted_timestamp, content=content)

    def create(self, task: Task) -> Task:
        task_dir = self._get_task_dir(task.id)
        task_dir.mkdir(parents=True, exist_ok=True)

        files = ["description.md", "design.md", "acceptance.md"]
        metadata = TaskMetadata(
            id=task.id,
            status=task.status,
            type=task.type,
            created=task.created,
            priority=task.priority,
            deps=task.deps,
            links=task.links,
            assignee=task.assignee,
            external_ref=task.external_ref,
            parent=task.parent,
            title=task.title,
            files=files
        )
        self._write_metadata(task_dir, metadata)

        self._write_markdown_file(task_dir, "description.md", task.description or "")
        self._write_markdown_file(task_dir, "design.md", task.design or "")
        self._write_markdown_file(task_dir, "acceptance.md", task.acceptance or "")

        return task

    def get(self, task_id: str) -> Task:
        task_dir = self._get_task_dir(task_id)
        if not task_dir.exists():
            raise TaskNotFoundError(f"task '{task_id}' not found")

        metadata = self._read_metadata(task_dir)
        description = self._read_markdown_file(task_dir, "description.md")
        design = self._read_markdown_file(task_dir, "design.md")
        acceptance = self._read_markdown_file(task_dir, "acceptance.md")
        notes = self._read_all_notes(task_dir)

        return Task(
            id=metadata.id,
            status=metadata.status,
            type=metadata.type,
            created=metadata.created,
            title=metadata.title,
            priority=metadata.priority,
            deps=metadata.deps,
            links=metadata.links,
            assignee=metadata.assignee,
            external_ref=metadata.external_ref,
            parent=metadata.parent,
            description=description,
            design=design,
            acceptance=acceptance,
            notes=notes
        )

    def find_by_partial_id(self, partial_id: str) -> Task:
        all_ids = self.get_all_ids()
        matcher = PartialIdMatcher(all_ids)
        resolved_id = matcher.resolve(partial_id)
        return self.get(resolved_id)

    def list_all(self) -> list[Task]:
        tasks: list[Task] = []
        for task_dir in self._get_all_task_dirs():
            task_id = task_dir.name
            task = self.get(task_id)
            tasks.append(task)
        return tasks

    def find_by_status(self, status: TaskStatus) -> list[Task]:
        return [task for task in self.list_all() if task.status == status]

    def find_ready(self) -> list[Task]:
        all_tasks = {task.id: task for task in self.list_all()}
        result: list[Task] = []
        for task in all_tasks.values():
            if task.status not in [TaskStatus.OPEN, TaskStatus.IN_PROGRESS]:
                continue
            if not task.deps:
                result.append(task)
                continue
            all_closed = all(
                dep_id in all_tasks and all_tasks[dep_id].status == TaskStatus.CLOSED
                for dep_id in task.deps
            )
            if all_closed:
                result.append(task)
        return result

    def find_blocked(self) -> list[Task]:
        all_tasks = {task.id: task for task in self.list_all()}
        result: list[Task] = []
        for task in all_tasks.values():
            if task.status not in [TaskStatus.OPEN, TaskStatus.IN_PROGRESS]:
                continue
            if not task.deps:
                continue
            has_unclosed = any(
                dep_id not in all_tasks or all_tasks[dep_id].status != TaskStatus.CLOSED
                for dep_id in task.deps
            )
            if has_unclosed:
                result.append(task)
        return result

    def find_recently_closed(self, limit: int = 20) -> list[Task]:
        closed_tasks = self.find_by_status(TaskStatus.CLOSED)
        with_mtime: list[tuple[float, Task]] = []
        for task in closed_tasks:
            task_dir = self._get_task_dir(task.id)
            mtime = task_dir.stat().st_mtime
            with_mtime.append((mtime, task))
        with_mtime.sort(key=lambda x: x[0], reverse=True)
        return [task for _, task in with_mtime[:limit]]

    def update(self, task: Task) -> Task:
        task_dir = self._get_task_dir(task.id)
        if not task_dir.exists():
            raise TaskNotFoundError(f"task '{task.id}' not found")

        metadata = self._read_metadata(task_dir)

        metadata.status = task.status
        metadata.priority = task.priority
        metadata.deps = task.deps
        metadata.links = task.links
        metadata.assignee = task.assignee
        metadata.external_ref = task.external_ref
        metadata.parent = task.parent
        metadata.title = task.title

        self._write_metadata(task_dir, metadata)

        self._write_markdown_file(task_dir, "description.md", task.description or "")
        self._write_markdown_file(task_dir, "design.md", task.design or "")
        self._write_markdown_file(task_dir, "acceptance.md", task.acceptance or "")

        return task

    def delete(self, task_id: str) -> None:
        task_dir = self._get_task_dir(task_id)
        if not task_dir.exists():
            raise TaskNotFoundError(f"task '{task_id}' not found")

        all_tasks = {task.id: task for task in self.list_all()}

        for task in all_tasks.values():
            updated = False
            if task_id in task.deps:
                task.deps = [dep for dep in task.deps if dep != task_id]
                updated = True
            if task_id in task.links:
                task.links = [link for link in task.links if link != task_id]
                updated = True
            if task.parent == task_id:
                task.parent = None
                updated = True
            if updated:
                self.update(task)

        shutil.rmtree(task_dir)

    def get_all_ids(self) -> list[str]:
        return [task_dir.name for task_dir in self._get_all_task_dirs()]

    def add_note_to_task(self, task_id: str, note_content: str) -> Task:
        from datetime import UTC

        task_dir = self._get_task_dir(task_id)
        if not task_dir.exists():
            raise TaskNotFoundError(f"task '{task_id}' not found")

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")[:-3]
        note_filename = f"note-{timestamp}.md"

        self._write_markdown_file(task_dir, note_filename, note_content)

        metadata = self._read_metadata(task_dir)
        if note_filename not in metadata.files:
            metadata.files.append(note_filename)
            self._write_metadata(task_dir, metadata)

        return self.get(task_id)
