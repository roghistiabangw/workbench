from __future__ import annotations

from collections.abc import Iterable

from .models import Note, Task, WorkbenchState, generate_short_id, utc_now
from .validation import normalize_tags, require_text, validate_task_priority, validate_task_status


def create_note(state: WorkbenchState, title: str, body: str, tags: list[str] | None = None) -> Note:
    existing_ids = {note.id for note in state.notes}
    now = utc_now()
    note = Note(
        id=generate_short_id("note", existing_ids),
        title=require_text(title, "title"),
        body=body,
        tags=normalize_tags(tags),
        created_at=now,
        updated_at=now,
    )
    state.notes.append(note)
    return note


def list_notes(state: WorkbenchState, include_archived: bool = False) -> list[Note]:
    return [note for note in state.notes if include_archived or not note.archived]


def get_note(state: WorkbenchState, note_id: str) -> Note:
    for note in state.notes:
        if note.id == note_id:
            return note
    raise ValueError(f"Unknown note ID: {note_id}")


def update_note(
    state: WorkbenchState,
    note_id: str,
    title: str | None = None,
    body: str | None = None,
    tags: list[str] | None = None,
) -> Note:
    note = get_note(state, note_id)
    if title is not None:
        note.title = require_text(title, "title")
    if body is not None:
        note.body = body
    if tags is not None:
        note.tags = normalize_tags(tags)
    note.updated_at = utc_now()
    return note


def archive_note(state: WorkbenchState, note_id: str) -> Note:
    note = get_note(state, note_id)
    note.archived = True
    note.updated_at = utc_now()
    return note


def restore_note(state: WorkbenchState, note_id: str) -> Note:
    note = get_note(state, note_id)
    note.archived = False
    note.updated_at = utc_now()
    return note


def create_task(
    state: WorkbenchState,
    title: str,
    priority: str = "normal",
    owner: str = "",
    due_date: str = "",
    tags: list[str] | None = None,
) -> Task:
    existing_ids = {task.id for task in state.tasks}
    now = utc_now()
    task = Task(
        id=generate_short_id("task", existing_ids),
        title=require_text(title, "title"),
        priority=validate_task_priority(priority),
        owner=owner,
        due_date=due_date,
        tags=normalize_tags(tags),
        created_at=now,
        updated_at=now,
    )
    state.tasks.append(task)
    return task


def list_tasks(state: WorkbenchState) -> list[Task]:
    return list(state.tasks)

