from __future__ import annotations

import json
from pathlib import Path

from .models import WorkbenchState


def import_state(current: WorkbenchState, incoming: WorkbenchState, mode: str = "merge") -> WorkbenchState:
    if mode not in ("merge", "replace"):
        raise ValueError(f"Unsupported import mode: {mode}")
    if mode == "replace":
        return incoming
    known = {
        "notes": {note.id for note in current.notes},
        "tasks": {task.id for task in current.tasks},
        "snippets": {snippet.id for snippet in current.snippets},
        "checklists": {checklist.id for checklist in current.checklists},
    }
    for note in incoming.notes:
        if note.id not in known["notes"]:
            current.notes.append(note)
    for task in incoming.tasks:
        if task.id not in known["tasks"]:
            current.tasks.append(task)
    for snippet in incoming.snippets:
        if snippet.id not in known["snippets"]:
            current.snippets.append(snippet)
    for checklist in incoming.checklists:
        if checklist.id not in known["checklists"]:
            current.checklists.append(checklist)
    return current


def import_state_file(current: WorkbenchState, path: Path, mode: str = "merge") -> WorkbenchState:
    data = json.loads(path.read_text(encoding="utf-8"))
    incoming = WorkbenchState.from_dict(data)
    return import_state(current, incoming, mode)


def export_state(state: WorkbenchState) -> dict:
    return state.to_dict()


def export_records(state: WorkbenchState, kinds: list[str] | None = None) -> dict:
    full = state.to_dict()
    if not kinds:
        return full
    allowed = {"notes", "tasks", "snippets", "checklists"}
    selected: dict = {}
    for kind in kinds:
        if kind not in allowed:
            raise ValueError(f"Unknown record kind: {kind}")
        selected[kind] = full[kind]
    return selected


def export_tasks_csv(state: WorkbenchState) -> str:
    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "status", "priority", "owner", "due_date"])
    for task in state.tasks:
        writer.writerow([task.id, task.title, task.status, task.priority, task.owner, task.due_date])
    return buffer.getvalue()


def export_notes_csv(state: WorkbenchState) -> str:
    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "tags"])
    for note in state.notes:
        writer.writerow([note.id, note.title, ";".join(note.tags)])
    return buffer.getvalue()
