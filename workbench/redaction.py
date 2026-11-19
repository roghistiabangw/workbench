from __future__ import annotations


def redact_export(data: dict, private_fields: list[str] | None = None) -> dict:
    fields = set(private_fields or ["owner", "source", "body"])
    redacted: dict = {}
    for kind, records in data.items():
        if not isinstance(records, list):
            redacted[kind] = records
            continue
        new_records = []
        for record in records:
            if isinstance(record, dict):
                clean = {key: ("[redacted]" if key in fields else value) for key, value in record.items()}
                new_records.append(clean)
            else:
                new_records.append(record)
        redacted[kind] = new_records
    return redacted
