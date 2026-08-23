from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorkbenchSettings:
    data_path: str = "workbench.json"
    date_format: str = "%Y-%m-%d"
    output_width: int = 80

    def to_dict(self) -> dict:
        return {
            "data_path": self.data_path,
            "date_format": self.date_format,
            "output_width": self.output_width,
        }


def default_settings() -> WorkbenchSettings:
    return WorkbenchSettings()


import json
from pathlib import Path


def validate_settings(data: dict) -> dict:
    allowed = {"data_path", "date_format", "output_width"}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"Unknown settings keys: {sorted(unknown)}")
    if "output_width" in data and int(data["output_width"]) <= 0:
        raise ValueError("output_width must be positive")
    return data


def load_settings(path: Path) -> WorkbenchSettings:
    if not path.exists():
        return WorkbenchSettings()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Settings file must contain a JSON object")
    validate_settings(data)
    return WorkbenchSettings(
        data_path=data.get("data_path", "workbench.json"),
        date_format=data.get("date_format", "%Y-%m-%d"),
        output_width=int(data.get("output_width", 80)),
    )
