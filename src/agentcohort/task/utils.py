from agentcohort.task.exceptions import AmbiguousTaskIdError, TaskNotFoundError
from agentcohort.task.models import Task


class PartialIdMatcher:
    def __init__(self, all_ids: list[str]) -> None:
        self.all_ids = all_ids

    def resolve(self, partial: str) -> str:
        matches = [task_id for task_id in self.all_ids if partial in task_id]
        if len(matches) == 0:
            raise TaskNotFoundError(f"task '{partial}' not found")
        if len(matches) == 1:
            return matches[0]
        raise AmbiguousTaskIdError(f"ambiguous id '{partial}' matches {', '.join(matches[:5])}")


class TreeVisualizer:
    def __init__(self, all_tasks: dict[str, Task]) -> None:
        self.all_tasks = all_tasks

    def visualize_tree(self, root_id: str, full_mode: bool = False) -> str:
        max_depths = self._calculate_max_depths(root_id)
        subtree_depths = self._calculate_subtree_depths(root_id, max_depths)
        output_lines: list[str] = []
        root = self.all_tasks[root_id]
        output_lines.append(f"{root.id} [{root.status.value}] {root.title}")
        self._build_tree_lines(
            root_id, max_depths, subtree_depths, output_lines, full_mode, "", "", set()
        )
        return "\n".join(output_lines)

    def _calculate_max_depths(self, root_id: str) -> dict[str, int]:
        max_depths = {root_id: 0}
        stack = [(root_id, 0)]
        while stack:
            current_id, depth = stack.pop()
            if current_id not in self.all_tasks:
                continue
            task = self.all_tasks[current_id]
            for dep_id in task.deps:
                if dep_id not in max_depths or depth + 1 > max_depths[dep_id]:
                    max_depths[dep_id] = depth + 1
                    stack.append((dep_id, depth + 1))
        return max_depths

    def _calculate_subtree_depths(self, root_id: str, max_depths: dict[str, int]) -> dict[str, int]:
        subtree_depths: dict[str, int] = {}
        stack = [(root_id, 0)]
        while stack:
            current_id, phase = stack.pop()
            if current_id not in self.all_tasks:
                continue
            if phase == 0:
                stack.append((current_id, 1))
                task = self.all_tasks[current_id]
                for dep_id in reversed(task.deps):
                    stack.append((dep_id, 0))
            else:
                task = self.all_tasks[current_id]
                children_depths = [max_depths[dep_id] for dep_id in task.deps if dep_id in max_depths]
                subtree_depths[current_id] = max([max_depths[current_id]] + children_depths)
        return subtree_depths

    def _build_tree_lines(
        self,
        task_id: str,
        max_depths: dict[str, int],
        subtree_depths: dict[str, int],
        output_lines: list[str],
        full_mode: bool,
        prefix: str,
        connector: str,
        printed: set[str],
    ) -> None:
        if task_id not in self.all_tasks:
            return
        task = self.all_tasks[task_id]
        children = task.deps
        if not full_mode and task_id != "" and task_id in printed:
            return
        if not full_mode and task_id != "" and max_depths[task_id] > subtree_depths[task_id]:
            printed.add(task_id)
        for idx, dep_id in enumerate(children):
            if dep_id not in self.all_tasks:
                continue
            dep = self.all_tasks[dep_id]
            is_last = idx == len(children) - 1
            current_prefix = prefix + ("│   " if not is_last else "    ")
            current_connector = connector + ("├── " if not is_last else "└── ")
            output_lines.append(f"{current_prefix}{current_connector}{dep.id} [{dep.status.value}] {dep.title}")
            self._build_tree_lines(
                dep_id, max_depths, subtree_depths, output_lines, full_mode, current_prefix, "", printed
            )
