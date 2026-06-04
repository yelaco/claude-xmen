#!/usr/bin/env python3
"""Validate Cerebro upgrade manifest and upgrade state metadata."""

import json
import re
from pathlib import Path


VALID_OWNERSHIPS = {"template", "merge", "user"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def main() -> int:
    errors = []
    errors.extend(validate_json_file(Path(".cerebro/schemas/upgrade-manifest.schema.json")))
    errors.extend(validate_json_file(Path(".cerebro/schemas/upgrade-state.schema.json")))
    errors.extend(validate_manifest())
    errors.extend(validate_state())

    if errors:
        for error in errors:
            print(error)
        return 1

    return 0


def validate_json_file(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path} missing"]
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path} invalid JSON: {exc}"]
    print(f"{path.name} valid")
    return []


def validate_manifest() -> list[str]:
    manifest_path = Path(".cerebro/upgrade-manifest.json")
    if not manifest_path.exists():
        print("no manifest present (informational - run /cerebro-upgrade to initialize)")
        return []

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"upgrade-manifest.json invalid JSON: {exc}"]
    errors = []
    entries = manifest.get("entries", [])
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty array")
        return errors

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry {index}: must be an object")
            continue
        if "path" not in entry:
            errors.append(f"entry {index}: missing 'path'")
        if "ownership" not in entry:
            errors.append(f"entry {index}: missing 'ownership'")
        elif entry["ownership"] not in VALID_OWNERSHIPS:
            errors.append(
                f"entry {index}: invalid ownership '{entry['ownership']}' "
                "(must be template, merge, or user)"
            )

    if not errors:
        print(f"manifest entries ok ({len(entries)} entries)")
    return errors


def validate_state() -> list[str]:
    state_path = Path(".cerebro/upgrade-state.json")
    if not state_path.exists():
        print("no upgrade-state.json present (informational - will be written after first /cerebro-upgrade)")
        return []

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"upgrade-state.json invalid JSON: {exc}"]
    errors = []
    required = {"version", "applied_ref", "applied_sha", "applied_at", "hashes"}
    missing = sorted(required - set(state))
    if missing:
        errors.append(f"upgrade-state.json missing fields: {missing}")
    if state.get("version") != 1:
        errors.append(f"unexpected version: {state.get('version')}")

    sha = state.get("applied_sha", "")
    if not SHA_RE.match(sha):
        errors.append(f"applied_sha is not a 40-char hex: {sha!r}")
    if not isinstance(state.get("hashes"), dict):
        errors.append("hashes must be an object")

    if not errors:
        print(f"upgrade-state.json valid (ref={state['applied_ref']}, sha={sha[:8]}...)")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
