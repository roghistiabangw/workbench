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


def repair_state(state: WorkbenchState) -> list[str]:
    actions: list[str] = []
    seen_ids: set[str] = set()
    for records in (state.notes, state.tasks, state.snippets, state.checklists):
        deduped = []
        for record in records:
            if record.id and record.id not in seen_ids:
                seen_ids.add(record.id)
                deduped.append(record)
            else:
                actions.append(f"removed duplicate or empty id: {record.id!r}")
        records[:] = deduped
    for task in state.tasks:
        if task.status not in ("todo", "doing", "blocked", "done"):
            actions.append(f"reset task {task.id} status to todo")
            task.status = "todo"
    return actions
