from __future__ import annotations

import argparse
from pathlib import Path

from .models import Note, Task, WorkbenchState
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
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--data", type=Path, default=Path("workbench.json"))
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("demo")
    subparsers.add_parser("summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
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


if __name__ == "__main__":
    raise SystemExit(main())
