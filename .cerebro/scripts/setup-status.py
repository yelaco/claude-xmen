#!/usr/bin/env python3
"""Wire CLAUDE.md and report Cerebro setup status."""

import argparse
import json
import subprocess
from pathlib import Path


IDENTITY_IMPORT = "@.cerebro/cerebro-identity.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", default="https://github.com/yelaco/claude-xmen.git")
    parser.add_argument("--skip-upstream", action="store_true")
    args = parser.parse_args()

    import_status = ensure_claude_import()
    identity_status = "PRESENT" if Path(".cerebro/cerebro-identity.md").is_file() else "MISSING"
    installed = installed_version()
    latest = "unreachable" if args.skip_upstream else latest_upstream_tag(args.upstream)
    upgrade_needed = compare_versions(installed, latest)

    if identity_status == "MISSING":
        print(
            ".cerebro/cerebro-identity.md not found. Run /cerebro-upgrade <latest-tag> "
            "to restore it - without this file the Cerebro runtime will not load."
        )

    if latest == "unreachable":
        print("Could not reach upstream - skipping version check. Check your connection and try again.")
    elif upgrade_needed == "NO":
        print(f"Cerebro installation is current at {installed}. No upgrade needed.")
    elif upgrade_needed == "YES":
        print(f"Upstream has {latest} - you are on {installed}. Run /cerebro-upgrade {latest} to sync.")
    else:
        print(
            f"Installed version is unknown (no upgrade-state.json). Latest upstream is {latest}. "
            f"Run /cerebro-upgrade {latest} to initialize upgrade tracking."
        )

    print()
    print("CLAUDE.md import     - " + import_status)
    print("cerebro-identity.md  - " + identity_status)
    print("installed version    - " + ("unknown" if installed == "none" else installed))
    print("latest upstream      - " + latest)
    print("upgrade needed       - " + upgrade_needed)
    print("semble integration   - ENABLED | SKIPPED | SKIPPED (no installer)")
    return 0


def ensure_claude_import() -> str:
    path = Path("CLAUDE.md")
    if not path.exists():
        path.write_text(IDENTITY_IMPORT + "\n", encoding="utf-8")
        return "FIXED"

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == IDENTITY_IMPORT:
        return "PRESENT"
    if IDENTITY_IMPORT in {line.strip() for line in lines}:
        return "PRESENT"

    path.write_text(IDENTITY_IMPORT + "\n\n" + text, encoding="utf-8")
    return "FIXED"


def installed_version() -> str:
    state_path = Path(".cerebro/upgrade-state.json")
    if not state_path.exists():
        return "none"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "unknown"
    return state.get("applied_ref", "unknown")


def latest_upstream_tag(upstream: str) -> str:
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--sort=-version:refname", upstream, "refs/tags/v*"],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unreachable"

    for line in result.stdout.splitlines():
        if "refs/tags/" in line:
            return line.rsplit("refs/tags/", 1)[1].removesuffix("^{}")
    return "unreachable"


def compare_versions(installed: str, latest: str) -> str:
    if latest == "unreachable":
        return "UNKNOWN"
    if installed in {"none", "unknown"}:
        return "UNKNOWN"
    if installed == latest:
        return "NO"
    return "YES"


if __name__ == "__main__":
    raise SystemExit(main())
