from abc import ABC, abstractmethod
from pathlib import Path

from agentcohort.task.exceptions import TaskNotFoundError
from agentcohort.task.models import Task, TaskStatus
from agentcohort.task.utils import MarkdownParser, PartialIdMatcher


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


class MarkdownTaskRepository(TaskRepository):
    def __init__(self, tasks_dir: Path) -> None:
        self.tasks_dir = tasks_dir
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, task_id: str) -> Path:
        return self.tasks_dir / f"{task_id}.md"

    def _get_all_file_paths(self) -> list[Path]:
        return sorted(self.tasks_dir.glob("*.md"))

    def create(self, task: Task) -> Task:
        file_path = self._get_file_path(task.id)
        MarkdownParser.write(file_path, task)
        return task

    def get(self, task_id: str) -> Task:
        file_path = self._get_file_path(task_id)
        if not file_path.exists():
            raise TaskNotFoundError(f"task '{task_id}' not found")
        return MarkdownParser.parse_to_task(file_path)

    def find_by_partial_id(self, partial_id: str) -> Task:
        all_ids = self.get_all_ids()
        matcher = PartialIdMatcher(all_ids)
        resolved_id = matcher.resolve(partial_id)
        return self.get(resolved_id)

    def list_all(self) -> list[Task]:
        tasks: list[Task] = []
        for file_path in self._get_all_file_paths():
            tasks.append(MarkdownParser.parse_to_task(file_path))
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
            file_path = self._get_file_path(task.id)
            mtime = file_path.stat().st_mtime
            with_mtime.append((mtime, task))
        with_mtime.sort(key=lambda x: x[0], reverse=True)
        return [task for _, task in with_mtime[:limit]]

    def update(self, task: Task) -> Task:
        file_path = self._get_file_path(task.id)
        if not file_path.exists():
            raise TaskNotFoundError(f"task '{task.id}' not found")
        MarkdownParser.write(file_path, task)
        return task

    def delete(self, task_id: str) -> None:
        file_path = self._get_file_path(task_id)
        if not file_path.exists():
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
                MarkdownParser.write(self._get_file_path(task.id), task)

        file_path.unlink()

    def get_all_ids(self) -> list[str]:
        return [task.id for task in self.list_all()]
