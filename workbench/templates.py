from __future__ import annotations


def note_template(topic: str) -> dict:
    return {"title": f"{topic} notes", "body": "", "tags": [topic.strip().lower()]}


def task_template(topic: str) -> dict:
    return {"title": f"Plan {topic}", "priority": "normal", "tags": [topic.strip().lower()]}


def checklist_template(name: str) -> dict:
    return {
        "name": name,
        "description": f"Checklist for {name}",
        "items": ["Define scope", "Do the work", "Review"],
    }
