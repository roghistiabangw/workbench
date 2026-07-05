# Workbench

Workbench is a small Python toolkit for local notes, tasks, snippets, project
checklists, and lightweight reports. It is intentionally dependency-free and
stores data in JSON so the project can stay easy to inspect, test, and extend.

## Quick Start

```bash
python -m workbench.cli demo
python -m workbench.cli summary
```

## Project Shape

- `workbench/models.py` contains the domain records.
- `workbench/storage.py` handles JSON loading and saving.
- `workbench/cli.py` provides the command line entrypoint.
- `tests/` contains standard-library unit tests.

The repository is planned as an incremental multi-file project. Each stage
should make one cohesive improvement and keep tests passing.
