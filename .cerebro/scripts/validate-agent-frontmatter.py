#!/usr/bin/env python3
"""Validate native Claude Code agent frontmatter."""

from pathlib import Path


REQUIRED_AGENTS = {
    "professor-x",
    "beast",
    "emma-frost",
    "cyclops",
    "wolverine",
    "forge",
    "nightcrawler",
    "sage",
    "storm",
}
VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
REQUIRED_KEYS = {"name", "description", "model", "effort", "tools"}


def main() -> int:
    failed = []
    seen = set()

    for path in sorted(Path(".claude/agents").glob("*.md")):
        text = path.read_text()
        if not text.startswith("---\n"):
            failed.append((str(path), "missing frontmatter"))
            continue
        end = text.find("\n---\n", 4)
        if end == -1:
            failed.append((str(path), "unterminated frontmatter"))
            continue

        frontmatter = {}
        for line in text[4:end].splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

        missing = sorted(REQUIRED_KEYS - set(frontmatter))
        if missing:
            failed.append((str(path), f"missing {missing}"))
            continue

        name = frontmatter["name"]
        seen.add(name)
        if name not in REQUIRED_AGENTS:
            failed.append((str(path), f"unexpected agent {name}"))
        if frontmatter["effort"] not in VALID_EFFORTS:
            failed.append((str(path), f"invalid effort {frontmatter['effort']}"))

        tools = {tool.strip() for tool in frontmatter["tools"].split(",")}
        if "Agent" in tools:
            failed.append((str(path), "Agent tool must not be allowed in subagents"))

    missing_agents = sorted(REQUIRED_AGENTS - seen)
    if missing_agents:
        failed.append((".claude/agents", f"missing agents {missing_agents}"))

    if failed:
        for item in failed:
            print(item)
        return 1

    print("native agent frontmatter ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
