from __future__ import annotations

from .models import WorkbenchState

PRIORITY_RANK = {"urgent": 0, "high": 1, "normal": 2, "low": 3}


def suggest_next_actions(state: WorkbenchState, limit: int = 3) -> list:
    open_tasks = [task for task in state.tasks if task.status != "done"]

    def sort_key(task):
        blocked = 0 if task.status == "blocked" else 1
        return (blocked, PRIORITY_RANK.get(task.priority, 2), task.due_date or "9999-99-99")

    ranked = sorted(open_tasks, key=sort_key)
    return [task.id for task in ranked[:limit]]
