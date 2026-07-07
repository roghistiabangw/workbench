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

