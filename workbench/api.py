"""Aggregated import surface for workbench services and helpers."""
from __future__ import annotations

from . import services
from .models import WorkbenchState
from .storage import load_state, save_state


def load(path) -> WorkbenchState:
    return load_state(path)


def save(path, state: WorkbenchState) -> None:
    save_state(path, state)
