from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import (
    Note,
    Task,
    Snippet,
    ProjectChecklist,
    ChecklistItem,
    WorkbenchState,
)
from .storage import load_state, save_state
from .services import (
    list_notes,
    create_note,
)


def demo_state() -> WorkbenchState:
    return WorkbenchState(
        notes=[
            Note(
                id="note-demo",
                title="First note",
                body="Capture useful project thoughts here.",
                tags=["demo", "notes"],
            )
        ],
        tasks=[
            Task(
                id="task-demo",
                title="Review the workbench plan",
                priority="high",
                tags=["demo", "planning"],
            )
        ],
        snippets=[
            Snippet(
                id="snippet-1",
                title="Python hello",
                language="python",
                body="print('Hello, World!')",
                tags=["hello", "demo"],
            )
        ],
        checklists=[
            ProjectChecklist(
                id="cl-demo",
                name="Demo checklist",
                description="Sample items for the demo state.",
                status="active",
                items=[
                    ChecklistItem(id="ci-1", text="Clone repo", done=False),
                    ChecklistItem(id="ci-2", text="Install deps", done=True),
                ],
            )
        ],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--data", type=Path, default=Path("workbench.json"))
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("demo")
    subparsers.add_parser("summary")
    demo_print = subparsers.add_parser("demo-print")
    demo_print.set_defaults(_print_demo=True)

    notes_cmd = subparsers.add_parser("notes")
    tasks_cmd = subparsers.add_parser("tasks")
    snippets_cmd = subparsers.add_parser("snippets")
    checklists_cmd = subparsers.add_parser("checklists")

    note_add = subparsers.add_parser("note-add")
    note_add.add_argument("--title", required=True)
    note_add.add_argument("--body", default="")
    note_add.add_argument("--tag", action="append", default=[])
    subparsers.add_parser("note-list")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "_print_demo", False):
        state = demo_state()
        print(json.dumps(state_to_dict(state), ensure_ascii=False, indent=2))
        return 0

    if args.command == "demo":
        save_state(args.data, demo_state())
        print(f"Demo state saved to {args.data}")
        return 0
    if args.command == "summary":
        state = load_state(args.data)
        print(
            f"notes={len(state.notes)} tasks={len(state.tasks)} "
            f"snippets={len(state.snippets)} checklists={len(state.checklists)}"
        )
        return 0

    if args.command == "notes":
        state = load_state(args.data)
        print(f"notes={len(state.notes)}")
        return 0
    if args.command == "tasks":
        state = load_state(args.data)
        print(f"tasks={len(state.tasks)}")
        return 0
    if args.command == "snippets":
        state = load_state(args.data)
        print(f"snippets={len(state.snippets)}")
        return 0
    if args.command == "checklists":
        state = load_state(args.data)
        print(f"checklists={len(state.checklists)}")
        return 0


    if args.command == "note-add":
        state = load_state(args.data)
        note = create_note(state, args.title, args.body, args.tag)
        save_state(args.data, state)
        print(note.id)
        return 0
    if args.command == "note-list":
        state = load_state(args.data)
        for note in list_notes(state):
            print(f"{note.id} {note.title}")
        return 0

    parser.print_help()
    return 0


def state_to_dict(state: WorkbenchState) -> dict:
    return state.to_dict()


if __name__ == "__main__":
    raise SystemExit(main())
