class TaskError(Exception):
    pass


class TaskNotFoundError(TaskError):
    pass


class AmbiguousTaskIdError(TaskError):
    pass


class InvalidTaskStatusError(TaskError):
    pass


class CircularDependencyError(TaskError):
    pass
