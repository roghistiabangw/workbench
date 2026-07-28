from __future__ import annotations

from datetime import date, datetime


def parse_date(value: str) -> date:
    text = value.strip()
    if not text:
        raise ValueError("date is required")
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid date: {value!r}") from exc


def format_date(value: date) -> str:
    return value.isoformat()


def days_until(target: str, today: date | None = None) -> int:
    reference = today or datetime.now().date()
    return (parse_date(target) - reference).days


def is_overdue(target: str, today: date | None = None) -> bool:
    return days_until(target, today) < 0
