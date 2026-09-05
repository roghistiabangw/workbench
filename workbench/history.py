from __future__ import annotations

import copy


class UndoStack:
    def __init__(self, limit: int = 20) -> None:
        self.limit = limit
        self._snapshots: list = []

    def snapshot(self, value) -> None:
        self._snapshots.append(copy.deepcopy(value))
        if len(self._snapshots) > self.limit:
            self._snapshots.pop(0)

    def can_undo(self) -> bool:
        return bool(self._snapshots)

    def undo(self):
        if not self._snapshots:
            raise ValueError("Nothing to undo")
        return self._snapshots.pop()
