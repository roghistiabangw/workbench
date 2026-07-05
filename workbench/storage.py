from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import WorkbenchState


def state_to_dict(state: WorkbenchState) -> dict[str, Any]:
    return asdict(state)


def load_state(path: Path) -> WorkbenchState:
    if not path.exists():
        return WorkbenchState()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Workbench state must be a JSON object")
    return WorkbenchState(schema_version=int(data.get("schema_version", 1)))


def save_state(path: Path, state: WorkbenchState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(state_to_dict(state), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)
