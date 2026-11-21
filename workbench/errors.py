from __future__ import annotations


class WorkbenchError(Exception):
    pass


class NotFoundError(WorkbenchError):
    pass


class ValidationError(WorkbenchError):
    pass


def friendly_message(error: Exception) -> str:
    if isinstance(error, NotFoundError):
        return f"Not found: {error}"
    if isinstance(error, ValidationError):
        return f"Invalid input: {error}"
    if isinstance(error, WorkbenchError):
        return f"Workbench error: {error}"
    return f"Unexpected error: {error}"
