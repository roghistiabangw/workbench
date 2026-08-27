from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def backup_name(now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    return f"workbench-{stamp}.json"


def create_backup(source: Path, backup_dir: Path, now: datetime | None = None) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / backup_name(now)
    if source.exists():
        shutil.copyfile(source, target)
    else:
        target.write_text("{}", encoding="utf-8")
    return target
