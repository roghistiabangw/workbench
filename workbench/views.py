from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SavedView:
    name: str
    record_type: str
    filters: dict = field(default_factory=dict)


def add_view(views: list, view: SavedView) -> list:
    if any(existing.name == view.name for existing in views):
        raise ValueError(f"View already exists: {view.name}")
    views.append(view)
    return views


def find_view(views: list, name: str) -> SavedView:
    for view in views:
        if view.name == name:
            return view
    raise ValueError(f"Unknown view: {name}")
