from __future__ import annotations

from .models import WorkbenchState


def daily_review(state: WorkbenchState) -> dict:
    open_tasks = [task for task in state.tasks if task.status != "done"]
    active_checklists = [checklist for checklist in state.checklists if checklist.status == "active"]
    return {
        "open_tasks": len(open_tasks),
        "active_checklists": len(active_checklists),
        "notes": len(state.notes),
        "snippets": len(state.snippets),
    }


def weekly_report(state: WorkbenchState) -> dict:
    done = [task for task in state.tasks if task.status == "done"]
    checklist_progress = 0
    if state.checklists:
        checklist_progress = round(
            sum(checklist.progress_percent for checklist in state.checklists) / len(state.checklists)
        )
    return {
        "tasks_done": len(done),
        "notes_total": len(state.notes),
        "snippets_total": len(state.snippets),
        "avg_checklist_progress": checklist_progress,
    }


def export_markdown(state: WorkbenchState) -> str:
    lines = ["# Workbench Report", ""]
    lines.append(f"- Notes: {len(state.notes)}")
    lines.append(f"- Tasks: {len(state.tasks)}")
    lines.append(f"- Snippets: {len(state.snippets)}")
    lines.append(f"- Checklists: {len(state.checklists)}")
    return "\n".join(lines) + "\n"
