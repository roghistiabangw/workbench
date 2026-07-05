from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .models import WorkbenchState


def state_to_dict(state: WorkbenchState) -> dict[str, Any]:
    return state.to_dict()


def load_state(path: Path) -> WorkbenchState:
    if not path.exists():
        return WorkbenchState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Invalid workbench state content: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Workbench state must be a JSON object")
    try:
        return WorkbenchState.from_dict(data)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid workbench state content: {exc}") from exc


def save_state(path: Path, state: WorkbenchState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        content = json.dumps(state_to_dict(state), ensure_ascii=False, indent=2) + "\n"
        temp_path.write_text(content, encoding="utf-8")
        os.replace(temp_path, path)
    except OSError as exc:
        raise ValueError(f"Failed to write workbench state: {exc}") from exc
