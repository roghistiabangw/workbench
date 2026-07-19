from __future__ import annotations

from collections.abc import Iterable

from .models import Note, Task, WorkbenchState, generate_short_id, utc_now, Snippet
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


def get_task(state: WorkbenchState, task_id: str) -> Task:
    for task in state.tasks:
        if task.id == task_id:
            return task
    raise ValueError(f"Unknown task ID: {task_id}")


def update_task_status(state: WorkbenchState, task_id: str, status: str) -> Task:
    task = get_task(state, task_id)
    task.status = validate_task_status(status)
    task.updated_at = utc_now()
    return task


def filter_tasks(
    state: WorkbenchState,
    status: str | None = None,
    owner: str | None = None,
    priority: str | None = None,
    tag: str | None = None,
    due_from: str | None = None,
    due_to: str | None = None,
) -> list[Task]:
    tasks = list_tasks(state)
    if status:
        validate_task_status(status)
        tasks = [task for task in tasks if task.status == status]
    if owner:
        tasks = [task for task in tasks if task.owner == owner]
    if priority:
        validate_task_priority(priority)
        tasks = [task for task in tasks if task.priority == priority]
    if tag:
        normalized = normalize_tags([tag])[0]
        tasks = [task for task in tasks if normalized in task.tags]
    if due_from:
        tasks = [task for task in tasks if task.due_date and task.due_date >= due_from]
    if due_to:
        tasks = [task for task in tasks if task.due_date and task.due_date <= due_to]
    return tasks


def task_summary_counts(state: WorkbenchState) -> dict[str, dict[str, int]]:
    summary = {
        "status": {},
        "priority": {},
        "owner": {},
    }
    for task in state.tasks:
        summary["status"][task.status] = summary["status"].get(task.status, 0) + 1
        summary["priority"][task.priority] = summary["priority"].get(task.priority, 0) + 1
        owner = task.owner or "unassigned"
        summary["owner"][owner] = summary["owner"].get(owner, 0) + 1
    return summary


def create_snippet(state: WorkbenchState, title: str, language: str, body: str, tags: list[str] | None = None, source: str = "") -> Snippet:
    existing_ids = {snippet.id for snippet in state.snippets}
    new_snippet = Snippet(
        id=generate_short_id("snip", existing_ids),
        title=require_text(title, "title"),
        language=require_text(language, "language"),
        body=body,
        tags=normalize_tags(tags),
        source=source,
        created_at=utc_now(),
    )
    state.snippets.append(new_snippet)
    return new_snippet


def list_snippets(state: WorkbenchState) -> list[Snippet]:
    return list(state.snippets)

