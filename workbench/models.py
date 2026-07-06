from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
from typing import Any, Iterable


TASK_STATUSES = ("todo", "doing", "blocked", "done")
TASK_PRIORITIES = ("low", "normal", "high", "urgent")
CHECKLIST_STATUSES = ("active", "paused", "complete", "archived")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_short_id(prefix: str, existing_ids: Iterable[str] | None = None, size: int = 8) -> str:
    clean_prefix = prefix.strip().lower().replace("_", "-")
    if not clean_prefix:
        raise ValueError("ID prefix is required")
    taken = set(existing_ids or [])
    while True:
        candidate = f"{clean_prefix}-{uuid.uuid4().hex[:size]}"
        if candidate not in taken:
            return candidate


@dataclass
class Note:
    id: str
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    archived: bool = False
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @property
    def is_active(self) -> bool:
        return not self.archived

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "tags": list(self.tags),
            "archived": self.archived,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        note = cls(
            id=data["id"],
            title=data["title"],
            body=data["body"],
            tags=list(data.get("tags", [])),
            archived=bool(data.get("archived", False)),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
        return note


@dataclass
class Task:
    id: str
    title: str
    status: str = "todo"
    priority: str = "normal"
    owner: str = ""
    due_date: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @property
    def is_complete(self) -> bool:
        return self.status == "done"

    @property
    def is_blocked(self) -> bool:
        return self.status == "blocked"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "owner": self.owner,
            "due_date": self.due_date,
            "tags": list(self.tags),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        task = cls(
            id=data["id"],
            title=data["title"],
            status=data.get("status", "todo"),
            priority=data.get("priority", "normal"),
            owner=data.get("owner", ""),
            due_date=data.get("due_date", ""),
            tags=list(data.get("tags", [])),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
        return task


@dataclass
class Snippet:
    id: str
    title: str
    language: str
    body: str
    tags: list[str] = field(default_factory=list)
    source: str = ""
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "language": self.language,
            "body": self.body,
            "tags": list(self.tags),
            "source": self.source,
            "created_at": self.created_at,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snippet":
        snippet = cls(
            id=data["id"],
            title=data["title"],
            language=data["language"],
            body=data["body"],
            tags=list(data.get("tags", [])),
            source=data.get("source", ""),
            created_at=data.get("created_at", ""),
        )
        return snippet


@dataclass
class ChecklistItem:
    id: str
    text: str
    done: bool = False
    blocked: bool = False

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "text": self.text,
            "done": self.done,
            "blocked": self.blocked,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChecklistItem":
        item = cls(
            id=data["id"],
            text=data["text"],
            done=bool(data.get("done", False)),
            blocked=bool(data.get("blocked", False)),
        )
        return item


@dataclass
class ProjectChecklist:
    id: str
    name: str
    description: str = ""
    status: str = "active"
    items: list[ChecklistItem] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def completed_items(self) -> int:
        return sum(1 for item in self.items if item.done)

    @property
    def progress_percent(self) -> int:
        if not self.items:
            return 0
        return round(self.completed_items / self.total_items * 100)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectChecklist":
        items = [ChecklistItem.from_dict(item) for item in data.get("items", [])]
        checklist = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            status=data.get("status", "active"),
            items=items,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
        return checklist


@dataclass
class WorkbenchState:
    notes: list[Note] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    snippets: list[Snippet] = field(default_factory=list)
    checklists: list[ProjectChecklist] = field(default_factory=list)
    schema_version: int = 1

    def summary_counts(self) -> dict[str, int]:
        return {
            "notes": len(self.notes),
            "tasks": len(self.tasks),
            "snippets": len(self.snippets),
            "checklists": len(self.checklists),
        }

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "notes": [note.to_dict() for note in self.notes],
            "tasks": [task.to_dict() for task in self.tasks],
            "snippets": [snippet.to_dict() for snippet in self.snippets],
            "checklists": [cl.to_dict() for cl in self.checklists],
            "schema_version": self.schema_version,
        }
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkbenchState":
        notes = [Note.from_dict(n) for n in data.get("notes", [])]
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        snippets = [Snippet.from_dict(s) for s in data.get("snippets", [])]
        checklists = [ProjectChecklist.from_dict(c) for c in data.get("checklists", [])]
        state = cls(
            notes=notes,
            tasks=tasks,
            snippets=snippets,
            checklists=checklists,
            schema_version=data.get("schema_version", 1),
        )
        return state
