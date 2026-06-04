#!/usr/bin/env python3
"""Validate Claude Code agent-team settings."""

import json
from pathlib import Path


def main() -> int:
    settings = json.loads(Path(".claude/settings.json").read_text())
    env = settings.get("env", {})
    if env.get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS") != "1":
        print("missing CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1")
        return 1
    print("agent teams enabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
