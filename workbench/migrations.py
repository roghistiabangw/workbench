from __future__ import annotations

CURRENT_SCHEMA_VERSION = 1


def migrate_state(data: dict) -> dict:
    version = int(data.get("schema_version", 1))
    if version > CURRENT_SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version: {version}")
    migrated = dict(data)
    migrated["schema_version"] = CURRENT_SCHEMA_VERSION
    return migrated
