from __future__ import annotations

from .models import CHECKLIST_STATUSES, TASK_PRIORITIES, TASK_STATUSES


def require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def normalize_tags(tags: list[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags or []:
        cleaned = tag.strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)
    return normalized


def validate_task_status(status: str) -> str:
    if status not in TASK_STATUSES:
        raise ValueError(f"Unsupported task status: {status}")
    return status


def validate_task_priority(priority: str) -> str:
    if priority not in TASK_PRIORITIES:
        raise ValueError(f"Unsupported task priority: {priority}")
    return priority


def validate_checklist_status(status: str) -> str:
    if status not in CHECKLIST_STATUSES:
        raise ValueError(f"Unsupported checklist status: {status}")
    return status
