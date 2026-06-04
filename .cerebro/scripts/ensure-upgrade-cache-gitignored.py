#!/usr/bin/env python3
"""Ensure .cerebro/.gitignore ignores Cerebro upgrade cache files."""

from pathlib import Path


LINE = "upgrade-cache/"


def main() -> int:
    path = Path(".cerebro/.gitignore")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.splitlines()
    if LINE in lines:
        print("upgrade cache already ignored")
        return 0

    prefix = text
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    path.write_text(prefix + LINE + "\n", encoding="utf-8")
    print("added upgrade-cache/ to .cerebro/.gitignore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
