from __future__ import annotations

from datetime import date, timedelta


def next_occurrence(start: date, schedule: str) -> date:
    if schedule == "daily":
        return start + timedelta(days=1)
    if schedule == "weekly":
        return start + timedelta(weeks=1)
    if schedule == "monthly":
        month = start.month + 1
        year = start.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(start.day, 28)
        return date(year, month, day)
    raise ValueError(f"Unsupported schedule: {schedule}")


def generate_occurrences(start: date, schedule: str, count: int) -> list:
    occurrences = []
    current = start
    for _ in range(max(0, count)):
        current = next_occurrence(current, schedule)
        occurrences.append(current)
    return occurrences
