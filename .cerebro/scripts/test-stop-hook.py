#!/usr/bin/env python3
"""Exercise Stop hook blocking behavior with a temporary task-scoped todo."""

import subprocess
from pathlib import Path


TODO_FILE = Path(".cerebro/pending-todos/doctor/worker/task.txt")


def main() -> int:
    previous = None
    if TODO_FILE.exists():
        previous = TODO_FILE.read_bytes()

    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    TODO_FILE.write_text("doctor temporary todo\n", encoding="utf-8")
    result = subprocess.run(
        ["bash", ".claude/hooks/check-pending-todos.sh"],
        capture_output=True,
        text=True,
        check=False,
    )

    if previous is None:
        TODO_FILE.unlink(missing_ok=True)
        _remove_empty_parents(TODO_FILE.parent)
    else:
        TODO_FILE.write_bytes(previous)

    if result.returncode != 0:
        print(result.stderr, end="")
        print(result.stdout, end="")
        return result.returncode
    if '"decision": "block"' not in result.stdout:
        print("expected Stop hook to return a block decision")
        print(result.stdout, end="")
        return 1

    print("block decision ok")
    return 0


def _remove_empty_parents(path: Path) -> None:
    root = Path(".cerebro/pending-todos")
    current = path
    while current != root.parent and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        if current == root:
            break
        current = current.parent


if __name__ == "__main__":
    raise SystemExit(main())
