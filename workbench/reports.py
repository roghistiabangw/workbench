from __future__ import annotations

from .models import WorkbenchState


def daily_review(state: WorkbenchState) -> dict:
    open_tasks = [task for task in state.tasks if task.status != "done"]
    active_checklists = [checklist for checklist in state.checklists if checklist.status == "active"]
    return {
        "open_tasks": len(open_tasks),
        "active_checklists": len(active_checklists),
        "notes": len(state.notes),
        "snippets": len(state.snippets),
    }
