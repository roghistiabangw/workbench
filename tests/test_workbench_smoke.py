import tempfile
import unittest
from pathlib import Path

from workbench.cli import demo_state, main
from workbench.models import ChecklistItem, ProjectChecklist, Task, WorkbenchState
from workbench.storage import load_state, save_state


class WorkbenchSmokeTests(unittest.TestCase):
    def test_demo_state_has_records(self) -> None:
        state = demo_state()

        self.assertEqual(len(state.notes), 1)
        self.assertEqual(len(state.tasks), 1)

    def test_save_and_load_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            save_state(path, WorkbenchState())
            loaded = load_state(path)

        self.assertEqual(loaded.schema_version, 1)

    def test_demo_command_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            result = main(["--data", str(path), "demo"])
            exists = path.exists()

        self.assertEqual(result, 0)
        self.assertTrue(exists)

    def test_task_state_helpers_preserve_defaults(self) -> None:
        task = Task(id="task-1", title="Review")

        self.assertEqual(task.status, "todo")
        self.assertFalse(task.is_complete)
        self.assertFalse(task.is_blocked)

    def test_checklist_progress_helpers(self) -> None:
        checklist = ProjectChecklist(
            id="check-1",
            name="Launch",
            items=[
                ChecklistItem(id="item-1", text="Draft", done=True),
                ChecklistItem(id="item-2", text="Review"),
            ],
        )

        self.assertEqual(checklist.total_items, 2)
        self.assertEqual(checklist.completed_items, 1)
        self.assertEqual(checklist.progress_percent, 50)

    def test_state_summary_counts(self) -> None:
        state = WorkbenchState(tasks=[Task(id="task-1", title="Review")])

        self.assertEqual(
            state.summary_counts(),
            {"notes": 0, "tasks": 1, "snippets": 0, "checklists": 0},
        )


if __name__ == "__main__":
    unittest.main()
