from __future__ import annotations

from .models import WorkbenchState


def check_integrity(state: WorkbenchState) -> list[str]:
    problems: list[str] = []
    seen_ids: set[str] = set()
    for kind, records in (
        ("note", state.notes),
        ("task", state.tasks),
        ("snippet", state.snippets),
        ("checklist", state.checklists),
    ):
        for record in records:
            if not record.id:
                problems.append(f"{kind} with empty id")
                continue
            if record.id in seen_ids:
                problems.append(f"duplicate id: {record.id}")
            seen_ids.add(record.id)
    for task in state.tasks:
        if task.status not in ("todo", "doing", "blocked", "done"):
            problems.append(f"task {task.id} has invalid status {task.status}")
    return problems
