from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


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


@dataclass
class WorkbenchState:
    notes: list[Note] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    snippets: list[Snippet] = field(default_factory=list)
    checklists: list[ProjectChecklist] = field(default_factory=list)
    schema_version: int = 1
