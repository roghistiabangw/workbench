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
