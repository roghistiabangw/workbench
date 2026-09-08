import tempfile
import unittest
from pathlib import Path

from workbench import models as models_module
from workbench.cli import demo_state, main
from workbench.models import (
    ChecklistItem,
    generate_short_id,
    Note,
    ProjectChecklist,
    Snippet,
    Task,
    WorkbenchState,
)
from workbench.storage import load_state, save_state
from workbench.services import (
    UndoStack,
    describe_plan,
    plan_mutation,
    repair_state,
    check_integrity,
    CURRENT_SCHEMA_VERSION,
    migrate_state,
    restore_backup,
    backup_name,
    create_backup,
    export_notes_csv,
    export_tasks_csv,
    export_records,
    export_state,
    import_state,
    validate_settings,
    load_settings,
    default_settings,
    render_task_detail,
    render_note_detail,
    render_table,
    search_all,
    tag_summary,
    collect_tags,
    is_overdue,
    days_until,
    format_date,
    parse_date,
    recent_events,
    log_event,
    checklist_progress,
    set_checklist_item_done,
    list_checklist_items,
    add_checklist_item,
    list_checklists,
    create_checklist,
    export_snippets,
    search_snippets,
    list_snippets,
    create_snippet,
    task_summary_counts,
    filter_tasks,
    update_task_status,
    get_task,
    list_tasks,
    create_task,
    restore_note,
    archive_note,
    update_note,
    get_note,
    list_notes,
    create_note,
)
from workbench.validation import normalize_tags, require_text, validate_task_status


class WorkbenchSmokeTests(unittest.TestCase):
    def test_demo_state_has_records(self) -> None:
        state = demo_state()

        self.assertEqual(len(state.notes), 1)
        self.assertEqual(len(state.tasks), 1)
        self.assertEqual(len(state.snippets), 1)
        self.assertEqual(len(state.checklists), 1)

    def test_demo_note_has_expected_fields(self) -> None:
        state = demo_state()
        note = state.notes[0]

        self.assertEqual(note.id, "note-demo")
        self.assertEqual(note.title, "First note")
        self.assertIn("demo", note.tags)

    def test_demo_task_has_expected_fields(self) -> None:
        state = demo_state()
        task = state.tasks[0]

        self.assertEqual(task.id, "task-demo")
        self.assertEqual(task.title, "Review the workbench plan")
        self.assertEqual(task.priority, "high")

    def test_demo_snippet_has_expected_fields(self) -> None:
        state = demo_state()
        snippet = state.snippets[0]

        self.assertEqual(snippet.id, "snippet-1")
        self.assertEqual(snippet.title, "Python hello")
        self.assertEqual(snippet.language, "python")

    def test_demo_checklist_has_expected_fields(self) -> None:
        state = demo_state()
        checklist = state.checklists[0]

        self.assertEqual(checklist.id, "cl-demo")
        self.assertEqual(checklist.name, "Demo checklist")
        self.assertEqual(len(checklist.items), 2)
        self.assertFalse(checklist.items[0].done)
        self.assertTrue(checklist.items[1].done)

    def test_demo_command_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            result = main(["--data", str(path), "demo"])
            exists = path.exists()

        self.assertEqual(result, 0)
        self.assertTrue(exists)

    def test_demo_print_does_not_create_data_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            result = main(["--data", str(path), "demo-print"])
            exists = path.exists()

        self.assertEqual(result, 0)
        self.assertFalse(exists)

    def test_demo_print_output_is_json(self) -> None:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            main(["demo-print"])

        output = buf.getvalue().strip()
        self.assertIn("note-demo", output)
        self.assertIn("task-demo", output)
        self.assertIn("snippet-1", output)
        self.assertIn("cl-demo", output)


    def test_validation_helpers_normalize_and_validate(self) -> None:
        self.assertEqual(normalize_tags([" Work ", "work", "", "Bug"]), ["work", "bug"])
        self.assertEqual(require_text("  Title  ", "title"), "Title")
        self.assertEqual(validate_task_status("todo"), "todo")
        with self.assertRaises(ValueError):
            require_text(" ", "title")
        with self.assertRaises(ValueError):
            validate_task_status("later")

    def test_generate_short_id_uses_prefix(self) -> None:
        generated = generate_short_id("note", size=6)

        self.assertTrue(generated.startswith("note-"))
        self.assertEqual(len(generated), len("note-") + 6)

    def test_generate_short_id_avoids_existing_ids(self) -> None:
        class FakeUuid:
            def __init__(self, value: str) -> None:
                self.hex = value

        values = [FakeUuid("aaaaaaaa"), FakeUuid("bbbbbbbb")]
        original_uuid4 = models_module.uuid.uuid4
        models_module.uuid.uuid4 = lambda: values.pop(0)
        try:
            generated = generate_short_id("task", existing_ids={"task-aaaaaaaa"})
        finally:
            models_module.uuid.uuid4 = original_uuid4

        self.assertEqual(generated, "task-bbbbbbbb")

    def test_generate_short_id_rejects_empty_prefix(self) -> None:
        with self.assertRaises(ValueError):
            generate_short_id("  ")

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

    def test_state_round_trip_preserves_all(self) -> None:
        notes = [Note(id="n-1", title="Hello", body="World")]
        tasks = [Task(id="t-1", title="Do it", status="doing", priority="high")]
        snippets = [Snippet(id="s-1", title="S", language="js", body="var x=1")]
        checklists = [
            ProjectChecklist(
                id="c-1",
                name="C",
                items=[
                    ChecklistItem(id="i-1", text="A", done=True),
                    ChecklistItem(id="i-2", text="B"),
                ],
            )
        ]

        state = WorkbenchState(
            notes=notes,
            tasks=tasks,
            snippets=snippets,
            checklists=checklists,
            schema_version=1,
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            save_state(path, state)
            loaded = load_state(path)

        self.assertEqual(loaded.schema_version, 1)
        self.assertEqual(len(loaded.notes), 1)
        self.assertEqual(loaded.notes[0].id, "n-1")
        self.assertEqual(len(loaded.tasks), 1)
        self.assertEqual(loaded.tasks[0].status, "doing")
        self.assertEqual(len(loaded.snippets), 1)
        self.assertEqual(len(loaded.checklists), 1)
        self.assertEqual(loaded.checklists[0].items[0].done, True)

    def test_save_load_with_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            state = WorkbenchState(
                notes=[Note(id="n-1", title="Saved", body="Content")],
                tasks=[Task(id="t-1", title="T", status="done")],
                snippets=[Snippet(id="s-1", title="S", language="py", body="print()")],
                checklists=[
                    ProjectChecklist(
                        id="c-1",
                        name="CL",
                        items=[
                            ChecklistItem(id="i-1", text="X", done=True),
                        ],
                    )
                ],
            )

            save_state(path, state)
            loaded = load_state(path)

        self.assertEqual(loaded.notes[0].title, "Saved")
        self.assertEqual(loaded.tasks[0].status, "done")
        self.assertEqual(loaded.snippets[0].language, "py")
        self.assertTrue(loaded.checklists[0].items[0].done)

    def test_load_missing_file_returns_empty_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nonexistent.json"

            loaded = load_state(path)

        self.assertEqual(len(loaded.notes), 0)
        self.assertEqual(len(loaded.tasks), 0)
        self.assertEqual(len(loaded.snippets), 0)
        self.assertEqual(len(loaded.checklists), 0)

    def test_load_invalid_json_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            path.write_text("{invalid json}", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_state(path)

    def test_saved_file_contains_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            save_state(path, WorkbenchState())

            content = path.read_text(encoding="utf-8")
            self.assertIn("notes", content)

    def test_save_state_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            nested_dir = Path(directory) / "nested" / "deep"
            path = nested_dir / "state.json"

            save_state(path, WorkbenchState())

            self.assertTrue(nested_dir.exists())

    def test_all_commands_return_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            main(["--data", str(path), "demo"])

            for command in ("notes", "tasks", "snippets", "checklists"):
                result = main(["--data", str(path), command])

        self.assertEqual(result, 0)
    def test_create_and_list_notes(self) -> None:
        state = WorkbenchState()
        note = create_note(state, " New note ", "Body", ["Work", "work"])

        self.assertEqual(note.title, "New note")
        self.assertEqual(note.tags, ["work"])
        self.assertEqual(list_notes(state), [note])

    def test_get_and_update_note(self) -> None:
        state = WorkbenchState()
        note = create_note(state, "Old", "Body")

        updated = update_note(state, note.id, title="New", tags=["A", "a"])

        self.assertEqual(get_note(state, note.id).title, "New")
        self.assertEqual(updated.tags, ["a"])
        with self.assertRaises(ValueError):
            get_note(state, "missing")

    def test_archive_and_restore_note(self) -> None:
        state = WorkbenchState()
        note = create_note(state, "Title", "Body")

        archive_note(state, note.id)
        self.assertEqual(list_notes(state), [])
        restore_note(state, note.id)
        self.assertEqual(list_notes(state), [note])

    def test_create_and_list_tasks(self) -> None:
        state = WorkbenchState()
        task = create_task(state, " Ship ", priority="high", owner="me", tags=["Launch"])

        self.assertEqual(task.title, "Ship")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.tags, ["launch"])
        self.assertEqual(list_tasks(state), [task])

    def test_update_task_status(self) -> None:
        state = WorkbenchState()
        task = create_task(state, "Ship")

        update_task_status(state, task.id, "doing")

        self.assertEqual(get_task(state, task.id).status, "doing")
        with self.assertRaises(ValueError):
            update_task_status(state, task.id, "later")

    def test_filter_tasks(self) -> None:
        state = WorkbenchState()
        first = create_task(state, "A", priority="high", owner="me", due_date="2030-01-01", tags=["Work"])
        create_task(state, "B", priority="low", owner="you", due_date="2030-02-01", tags=["Home"])

        self.assertEqual(filter_tasks(state, priority="high"), [first])
        self.assertEqual(filter_tasks(state, owner="me"), [first])
        self.assertEqual(filter_tasks(state, tag="work"), [first])
        self.assertEqual(filter_tasks(state, due_to="2030-01-15"), [first])

    def test_task_summary_counts(self) -> None:
        state = WorkbenchState()
        create_task(state, "A", priority="high", owner="me")
        other = create_task(state, "B", priority="low")
        update_task_status(state, other.id, "done")

        summary = task_summary_counts(state)

        self.assertEqual(summary["status"]["todo"], 1)
        self.assertEqual(summary["status"]["done"], 1)
        self.assertEqual(summary["owner"]["me"], 1)
        self.assertEqual(summary["owner"]["unassigned"], 1)

    def test_create_and_list_snippets(self) -> None:
        state = WorkbenchState()
        snippet = create_snippet(state, " Sort ", "python", "print(1)", ["Util", "util"])

        self.assertEqual(snippet.title, "Sort")
        self.assertEqual(snippet.language, "python")
        self.assertEqual(snippet.tags, ["util"])
        self.assertEqual(list_snippets(state), [snippet])

    def test_search_snippets(self) -> None:
        state = WorkbenchState()
        first = create_snippet(state, "Bubble sort", "python", "swap values")
        create_snippet(state, "HTTP client", "go", "send request")

        results = search_snippets(state, "SORT")

        self.assertEqual(results, [first])

    def test_export_snippets(self) -> None:
        state = WorkbenchState()
        snippet = create_snippet(state, "Sort", "python", "body", ["util"])

        exported = export_snippets(state)

        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0]["id"], snippet.id)
        self.assertEqual(exported[0]["language"], "python")

    def test_create_and_list_checklists(self) -> None:
        state = WorkbenchState()
        checklist = create_checklist(state, " Launch ", "Ship it")

        self.assertEqual(checklist.name, "Launch")
        self.assertEqual(checklist.description, "Ship it")
        self.assertEqual(list_checklists(state), [checklist])

    def test_add_checklist_items(self) -> None:
        state = WorkbenchState()
        checklist = create_checklist(state, "Launch")
        item = add_checklist_item(state, checklist.id, " Write docs ")

        self.assertEqual(item.text, "Write docs")
        self.assertFalse(item.done)
        self.assertEqual(list_checklist_items(state, checklist.id), [item])

    def test_checklist_progress_service(self) -> None:
        state = WorkbenchState()
        checklist = create_checklist(state, "Launch")
        first = add_checklist_item(state, checklist.id, "A")
        add_checklist_item(state, checklist.id, "B")

        set_checklist_item_done(state, checklist.id, first.id)
        progress = checklist_progress(state, checklist.id)

        self.assertEqual(progress["total"], 2)
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["percent"], 50)

    def test_activity_log_records_events(self) -> None:
        events: list[dict] = []
        log_event(events, "create", "note", "note-1")
        log_event(events, "update", "task", "task-9")

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["action"], "create")
        self.assertEqual(recent_events(events, 1)[0]["record_id"], "task-9")

    def test_date_utilities(self) -> None:
        from datetime import date

        self.assertEqual(format_date(parse_date(" 2026-01-02 ")), "2026-01-02")
        self.assertEqual(days_until("2026-01-10", date(2026, 1, 1)), 9)
        self.assertTrue(is_overdue("2025-12-31", date(2026, 1, 1)))
        with self.assertRaises(ValueError):
            parse_date("not-a-date")

    def test_tag_utilities(self) -> None:
        state = WorkbenchState()
        create_note(state, "N", "b", ["work", "urgent"])
        create_task(state, "T", tags=["work"])

        self.assertEqual(collect_tags(state), ["urgent", "work"])
        self.assertEqual(tag_summary(state)["work"], 2)

    def test_search_all(self) -> None:
        state = WorkbenchState()
        note = create_note(state, "Alpha plan", "body")
        create_task(state, "Beta task")

        results = search_all(state, "alpha")

        self.assertEqual(results["notes"], [note.id])
        self.assertEqual(results["tasks"], [])

    def test_render_table(self) -> None:
        table = render_table(["ID", "Title"], [["1", "Alpha"], ["22", "Beta"]])
        lines = table.splitlines()

        self.assertEqual(lines[0], "ID  Title")
        self.assertEqual(lines[2], "1   Alpha")

    def test_detail_renderers(self) -> None:
        state = WorkbenchState()
        note = create_note(state, "Title", "Body text", ["a"])
        task = create_task(state, "Do it", priority="high")

        note_detail = render_note_detail(note)
        task_detail = render_task_detail(task)

        self.assertIn("Note " + note.id, note_detail)
        self.assertIn("Body text", note_detail)
        self.assertIn("Priority: high", task_detail)

    def test_settings_defaults(self) -> None:
        settings = default_settings()

        self.assertEqual(settings.data_path, "workbench.json")
        self.assertEqual(settings.output_width, 80)
        self.assertEqual(settings.to_dict()["date_format"], "%Y-%m-%d")

    def test_load_settings(self) -> None:
        import json as _json
        import tempfile
        from pathlib import Path as _Path

        with tempfile.TemporaryDirectory() as tmp:
            path = _Path(tmp) / "cfg.json"
            path.write_text(_json.dumps({"output_width": 120}), encoding="utf-8")
            settings = load_settings(path)

        self.assertEqual(settings.output_width, 120)
        with self.assertRaises(ValueError):
            validate_settings({"bad": 1})

    def test_import_state_merge(self) -> None:
        current = WorkbenchState()
        create_note(current, "Keep", "body")
        incoming = WorkbenchState()
        create_note(incoming, "New", "body")

        merged = import_state(current, incoming, "merge")

        self.assertEqual(len(merged.notes), 2)
        replaced = import_state(current, incoming, "replace")
        self.assertEqual(len(replaced.notes), 1)

    def test_export_records_filtered(self) -> None:
        state = WorkbenchState()
        create_note(state, "N", "b")
        create_task(state, "T")

        only_notes = export_records(state, ["notes"])

        self.assertIn("notes", only_notes)
        self.assertNotIn("tasks", only_notes)
        self.assertEqual(len(export_state(state)["tasks"]), 1)

    def test_export_tasks_csv(self) -> None:
        state = WorkbenchState()
        create_task(state, "Task A", priority="high", owner="me")

        csv_text = export_tasks_csv(state)
        lines = csv_text.strip().splitlines()

        self.assertEqual(lines[0], "id,title,status,priority,owner,due_date")
        self.assertIn("Task A", lines[1])
        self.assertIn("high", lines[1])

    def test_create_backup(self) -> None:
        import tempfile
        from datetime import datetime, timezone
        from pathlib import Path as _Path

        with tempfile.TemporaryDirectory() as tmp:
            source = _Path(tmp) / "workbench.json"
            source.write_text("{}", encoding="utf-8")
            when = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
            backup = create_backup(source, _Path(tmp) / "backups", when)
            self.assertTrue(backup.exists())

        self.assertEqual(backup.name, "workbench-20260102-030405.json")

    def test_restore_backup(self) -> None:
        import json as _json
        import tempfile
        from pathlib import Path as _Path

        with tempfile.TemporaryDirectory() as tmp:
            backup = _Path(tmp) / "b.json"
            backup.write_text(_json.dumps({"schema_version": 1}), encoding="utf-8")
            target = _Path(tmp) / "restored.json"
            restore_backup(backup, target)
            restored = _json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(restored["schema_version"], 1)

    def test_migrate_state(self) -> None:
        migrated = migrate_state({"notes": [], "schema_version": 1})
        self.assertEqual(migrated["schema_version"], CURRENT_SCHEMA_VERSION)
        with self.assertRaises(ValueError):
            migrate_state({"schema_version": 999})

    def test_check_integrity(self) -> None:
        state = WorkbenchState()
        task = create_task(state, "Ok")
        self.assertEqual(check_integrity(state), [])
        state.tasks.append(task)
        problems = check_integrity(state)
        self.assertTrue(any("duplicate id" in problem for problem in problems))

    def test_repair_state(self) -> None:
        state = WorkbenchState()
        task = create_task(state, "Ok")
        state.tasks.append(task)
        actions = repair_state(state)
        self.assertEqual(len(state.tasks), 1)
        self.assertTrue(actions)

    def test_dry_run_plan(self) -> None:
        plan = plan_mutation("delete", "task-1", "no confirm")
        self.assertFalse(plan["applied"])
        self.assertEqual(describe_plan(plan), "DRY-RUN delete task-1 (no confirm)")

    def test_undo_stack(self) -> None:
        stack = UndoStack()
        self.assertFalse(stack.can_undo())
        stack.snapshot({"count": 1})
        stack.snapshot({"count": 2})
        self.assertEqual(stack.undo(), {"count": 2})
        self.assertEqual(stack.undo(), {"count": 1})
        with self.assertRaises(ValueError):
            stack.undo()

    def test_parser_has_description(self) -> None:
        from workbench.cli import build_parser

        parser = build_parser()

        self.assertTrue(parser.description)

    def test_note_update_and_validation(self) -> None:
        state = WorkbenchState()
        note = create_note(state, "Original", "body", ["x"])
        updated = update_note(state, note.id, title="Renamed")
        self.assertEqual(updated.title, "Renamed")
        with self.assertRaises(ValueError):
            create_note(state, "   ", "body")

    def test_task_workflow_and_filters(self) -> None:
        state = WorkbenchState()
        task = create_task(state, "Ship", priority="high", owner="me")
        update_task_status(state, task.id, "done")
        self.assertEqual(get_task(state, task.id).status, "done")
        results = filter_tasks(state, "done", None, None, None, None, None)
        self.assertEqual(results, [get_task(state, task.id)])



if __name__ == "__main__":
    unittest.main()
