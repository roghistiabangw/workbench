import tempfile
import unittest
from pathlib import Path

from workbench.cli import demo_state, main
from workbench.models import WorkbenchState
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


if __name__ == "__main__":
    unittest.main()
