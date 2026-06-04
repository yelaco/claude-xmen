#!/usr/bin/env python3
"""Validate Cerebro team-run manifest template and runtime manifests."""

import json
from pathlib import Path


ALLOWED_COMMANDS = {"/to-me-my-x-men", "/cerebro-plan", "/cerebro-start-work", "/cerebro-index"}
ALLOWED_STATUSES = {"planning", "running", "blocked", "completed", "cleaned_up"}
ALLOWED_RISKS = {"LOW", "MEDIUM", "HIGH"}
ALLOWED_AGENTS = {
    "cyclops",
    "wolverine",
    "storm",
    "professor-x",
    "beast",
    "emma-frost",
    "nightcrawler",
    "sage",
    "forge",
}
ALLOWED_TEAMMATE_STATUSES = {"pending", "active", "idle", "done", "blocked"}
ALLOWED_APPROVAL_STATUSES = {"pending", "approved", "rejected"}
ALLOWED_VERIFICATION_STATUSES = {"NOT RUN", "PASS", "FAIL", "BLOCKED"}


def main() -> int:
    paths = [
        Path(".cerebro/templates/team-run.json"),
        *sorted(Path(".cerebro/team-runs").glob("*.json")),
    ]

    errors = []
    for path in paths:
        errors.extend(validate_manifest(path))

    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"team run manifests schema ok ({len(paths)} file(s))")
    return 0


def validate_manifest(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    errors = []

    top_required = {
        "version",
        "run_id",
        "command",
        "status",
        "lead",
        "team_name",
        "objective",
        "risk_level",
        "started_at",
        "updated_at",
        "teammates",
        "ownership",
        "mailbox_decisions",
        "approvals",
        "verification",
        "cleanup",
    }
    errors.extend(_check_keys(str(path), data, top_required))

    if data.get("version") != 1:
        errors.append(f"{path}: version must be 1")
    if data.get("command") not in ALLOWED_COMMANDS:
        errors.append(f"{path}: invalid command {data.get('command')!r}")
    if data.get("status") not in ALLOWED_STATUSES:
        errors.append(f"{path}: invalid status {data.get('status')!r}")
    if data.get("lead") != "cerebro":
        errors.append(f"{path}: lead must be cerebro")
    if data.get("risk_level") not in ALLOWED_RISKS:
        errors.append(f"{path}: invalid risk_level {data.get('risk_level')!r}")
    for key in ("run_id", "team_name", "objective", "started_at", "updated_at"):
        errors.extend(_non_empty(f"{path}: {key}", data.get(key)))

    for field in ("teammates", "ownership", "mailbox_decisions", "approvals", "verification"):
        if not isinstance(data.get(field), list):
            errors.append(f"{path}: {field} must be an array")

    _validate_teammates(path, data.get("teammates", []), errors)
    _validate_ownership(path, data.get("ownership", []), errors)
    _validate_mailbox(path, data.get("mailbox_decisions", []), errors)
    _validate_approvals(path, data.get("approvals", []), errors)
    _validate_verification(path, data.get("verification", []), errors)
    _validate_cleanup(path, data.get("cleanup"), errors)

    return errors


def _validate_teammates(path: Path, items: list, errors: list[str]) -> None:
    required = {"name", "agent_type", "status", "responsibility", "last_signal"}
    for index, item in enumerate(items):
        label = f"{path}: teammates[{index}]"
        errors.extend(_check_keys(label, item, required))
        errors.extend(_non_empty(f"{label}.name", item.get("name")))
        if item.get("agent_type") not in ALLOWED_AGENTS:
            errors.append(f"{label}.agent_type invalid {item.get('agent_type')!r}")
        if item.get("status") not in ALLOWED_TEAMMATE_STATUSES:
            errors.append(f"{label}.status invalid {item.get('status')!r}")


def _validate_ownership(path: Path, items: list, errors: list[str]) -> None:
    required = {"path", "owner", "reviewer", "notes"}
    for index, item in enumerate(items):
        label = f"{path}: ownership[{index}]"
        errors.extend(_check_keys(label, item, required))
        errors.extend(_non_empty(f"{label}.path", item.get("path")))
        errors.extend(_non_empty(f"{label}.owner", item.get("owner")))


def _validate_mailbox(path: Path, items: list, errors: list[str]) -> None:
    required = {"at", "from", "to", "topic", "decision", "open"}
    for index, item in enumerate(items):
        label = f"{path}: mailbox_decisions[{index}]"
        errors.extend(_check_keys(label, item, required))
        for key in ("at", "from", "topic", "decision"):
            errors.extend(_non_empty(f"{label}.{key}", item.get(key)))
        if not isinstance(item.get("to"), list):
            errors.append(f"{label}.to must be an array")
        if not isinstance(item.get("open"), bool):
            errors.append(f"{label}.open must be a boolean")


def _validate_approvals(path: Path, items: list, errors: list[str]) -> None:
    required = {"gate", "status", "decided_at", "notes"}
    for index, item in enumerate(items):
        label = f"{path}: approvals[{index}]"
        errors.extend(_check_keys(label, item, required))
        errors.extend(_non_empty(f"{label}.gate", item.get("gate")))
        if item.get("status") not in ALLOWED_APPROVAL_STATUSES:
            errors.append(f"{label}.status invalid {item.get('status')!r}")


def _validate_verification(path: Path, items: list, errors: list[str]) -> None:
    required = {"command", "status", "by", "notes"}
    for index, item in enumerate(items):
        label = f"{path}: verification[{index}]"
        errors.extend(_check_keys(label, item, required))
        errors.extend(_non_empty(f"{label}.command", item.get("command")))
        errors.extend(_non_empty(f"{label}.by", item.get("by")))
        if item.get("status") not in ALLOWED_VERIFICATION_STATUSES:
            errors.append(f"{label}.status invalid {item.get('status')!r}")


def _validate_cleanup(path: Path, cleanup: object, errors: list[str]) -> None:
    required = {"team_stopped", "pending_todos_clear", "notes"}
    label = f"{path}: cleanup"
    if not isinstance(cleanup, dict):
        errors.append(f"{label} must be an object")
        return
    errors.extend(_check_keys(label, cleanup, required))
    for key in ("team_stopped", "pending_todos_clear"):
        if not isinstance(cleanup.get(key), bool):
            errors.append(f"{label}.{key} must be a boolean")


def _check_keys(label: str, item: object, required: set[str]) -> list[str]:
    if not isinstance(item, dict):
        return [f"{label}: must be an object"]
    errors = []
    missing = sorted(required - set(item))
    extra = sorted(set(item) - required)
    if missing:
        errors.append(f"{label}: missing {missing}")
    if extra:
        errors.append(f"{label}: unexpected {extra}")
    return errors


def _non_empty(label: str, value: object) -> list[str]:
    return [] if isinstance(value, str) and value else [f"{label}: must be a non-empty string"]


if __name__ == "__main__":
    raise SystemExit(main())
