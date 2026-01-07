from datetime import UTC, datetime

from agentcohort.task.exceptions import CircularDependencyError, TaskNotFoundError
from agentcohort.task.id_generator import TaskIdGenerator
from agentcohort.task.models import Note, Task, TaskStatus, TaskType
from agentcohort.task.repository import TaskRepository
from agentcohort.task.utils import TreeVisualizer


class TaskService:
    def __init__(self, repository: TaskRepository, id_generator: TaskIdGenerator) -> None:
        self.repository = repository
        self.id_generator = id_generator

    def create_task(
        self,
        title: str,
        description: str | None = None,
        design: str | None = None,
        acceptance: str | None = None,
        task_type: TaskType = TaskType.TASK,
        priority: int = 2,
        assignee: str | None = None,
        external_ref: str | None = None,
        parent: str | None = None,
    ) -> Task:
        if not 0 <= priority <= 4:
            raise ValueError("priority must be between 0 and 4")
        task_id = self.id_generator.generate()
        if parent:
            try:
                self.repository.find_by_partial_id(parent)
            except TaskNotFoundError:
                raise ValueError(f"parent task '{parent}' not found")
        created = datetime.now(UTC).isoformat()
        task = Task(
            id=task_id,
            status=TaskStatus.OPEN,
            type=task_type,
            priority=priority,
            deps=[],
            links=[],
            created=created,
            title=title,
            description=description,
            design=design,
            acceptance=acceptance,
            assignee=assignee,
            external_ref=external_ref,
            parent=parent,
            notes=[],
        )
        return self.repository.create(task)

    def set_status(self, task_id: str, status: TaskStatus) -> Task:
        task = self.repository.find_by_partial_id(task_id)
        task.status = status
        return self.repository.update(task)

    def start_task(self, task_id: str) -> Task:
        return self.set_status(task_id, TaskStatus.IN_PROGRESS)

    def close_task(self, task_id: str) -> Task:
        return self.set_status(task_id, TaskStatus.CLOSED)

    def reopen_task(self, task_id: str) -> Task:
        return self.set_status(task_id, TaskStatus.OPEN)

    def get_task(self, task_id: str) -> Task:
        return self.repository.find_by_partial_id(task_id)

    def list_tasks(self, status_filter: TaskStatus | None = None) -> list[Task]:
        if status_filter is not None:
            return self.repository.find_by_status(status_filter)
        return self.repository.list_all()

    def get_ready_tasks(self) -> list[Task]:
        tasks = self.repository.find_ready()
        return sorted(tasks, key=lambda t: (t.priority, t.id))

    def get_blocked_tasks(self) -> list[Task]:
        tasks = self.repository.find_blocked()
        return sorted(tasks, key=lambda t: (t.priority, t.id))

    def get_recently_closed_tasks(self, limit: int = 20) -> list[Task]:
        return self.repository.find_recently_closed(limit)

    def add_note(self, task_id: str, note_content: str) -> Task:
        task = self.repository.find_by_partial_id(task_id)
        timestamp = datetime.now(UTC).isoformat()
        note = Note(timestamp=timestamp, content=note_content)
        task.notes.append(note)
        return self.repository.update(task)


class DependencyService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def add_dependency(self, task_id: str, dep_id: str) -> Task:
        task = self.repository.find_by_partial_id(task_id)
        dep_task = self.repository.find_by_partial_id(dep_id)
        resolved_dep_id = dep_task.id
        if resolved_dep_id in task.deps:
            return task
        if self._detect_cycle(resolved_dep_id, task.id):
            raise CircularDependencyError(f"adding dependency would create cycle: {task_id} -> {dep_id}")
        task.deps.append(resolved_dep_id)
        return self.repository.update(task)

    def remove_dependency(self, task_id: str, dep_id: str) -> Task:
        task = self.repository.find_by_partial_id(task_id)
        dep_task = self.repository.find_by_partial_id(dep_id)
        resolved_dep_id = dep_task.id
        if resolved_dep_id not in task.deps:
            return task
        task.deps = [d for d in task.deps if d != resolved_dep_id]
        return self.repository.update(task)

    def get_dependency_tree(self, root_id: str, full_mode: bool = False) -> str:
        resolved_id = self.repository.find_by_partial_id(root_id).id
        all_tasks = {task.id: task for task in self.repository.list_all()}
        visualizer = TreeVisualizer(all_tasks)
        return visualizer.visualize_tree(resolved_id, full_mode)

    def _detect_cycle(self, start_id: str, target_id: str) -> bool:
        all_tasks = {task.id: task for task in self.repository.list_all()}
        visited: set[str] = set()
        stack: list[str] = [start_id]
        while stack:
            current_id = stack.pop()
            if current_id == target_id:
                return True
            if current_id in visited:
                continue
            visited.add(current_id)
            if current_id not in all_tasks:
                continue
            current_task = all_tasks[current_id]
            stack.extend(current_task.deps)
        return False


class LinkService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def link_tasks(self, task_ids: list[str]) -> int:
        if len(task_ids) < 2:
            raise ValueError("at least 2 tasks required for linking")
        tasks: dict[str, Task] = {}
        for tid in task_ids:
            task = self.repository.find_by_partial_id(tid)
            tasks[task.id] = task
        resolved_ids: list[str] = list(tasks.keys())
        added_count = 0
        for task_id in resolved_ids:
            task = tasks[task_id]
            other_ids: list[str] = [oid for oid in resolved_ids if oid != task_id]
            for other_id in other_ids:
                if other_id not in task.links:
                    task.links.append(other_id)
                    added_count += 1
            self.repository.update(task)
        return added_count

    def unlink_tasks(self, task_id: str, target_id: str) -> None:
        task1 = self.repository.find_by_partial_id(task_id)
        task2 = self.repository.find_by_partial_id(target_id)
        task1.links = [lid for lid in task1.links if lid != task2.id]
        task2.links = [lid for lid in task2.links if lid != task1.id]
        self.repository.update(task1)
        self.repository.update(task2)


class QueryService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def query_all(self) -> list[Task]:
        return self.repository.list_all()

    def query_filtered(self) -> list[Task]:
        return self.query_all()
