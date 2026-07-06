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

    parser.print_help()
    return 0


def state_to_dict(state: WorkbenchState) -> dict:
    return state.to_dict()


if __name__ == "__main__":
    raise SystemExit(main())
