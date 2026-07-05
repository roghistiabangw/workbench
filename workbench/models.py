from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


TASK_STATUSES = ("todo", "doing", "blocked", "done")
TASK_PRIORITIES = ("low", "normal", "high", "urgent")
CHECKLIST_STATUSES = ("active", "paused", "complete", "archived")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


@dataclass
class Snippet:
    id: str
    title: str
    language: str
    body: str
    tags: list[str] = field(default_factory=list)
    source: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass
class ChecklistItem:
    id: str
    text: str
    done: bool = False
    blocked: bool = False


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
