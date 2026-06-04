#!/bin/bash

python3 - <<'PYEOF'
import json
from pathlib import Path

todo_sources = []

legacy_file = Path(".cerebro/.pending-todos")
if legacy_file.is_file():
    todo_sources.append(legacy_file)

todo_root = Path(".cerebro/pending-todos")
if todo_root.is_dir():
    todo_sources.extend(sorted(p for p in todo_root.rglob("*") if p.is_file()))

items = []
for path in todo_sources:
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    except UnicodeDecodeError:
        lines = [line.strip() for line in path.read_text(errors="replace").splitlines()]
    for line in lines:
        if line:
            items.append((path, line))

if items:
    todo_list = "\n".join(f"  - [ ] {line} ({path})" for path, line in items)
    reason = (
        "\n[SYSTEM REMINDER - TODO CONTINUATION]\n\n"
        "You have incomplete todos! Complete ALL before responding:\n\n"
        f"{todo_list}\n\n"
        "DO NOT respond until all task-scoped todo files under .cerebro/pending-todos/ "
        "are removed or empty."
    )
    print(json.dumps({"decision": "block", "reason": reason}))
PYEOF

exit 0
