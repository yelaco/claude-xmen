#!/usr/bin/env python3
"""Atomically write .cerebro/upgrade-state.json from current owned file hashes."""

import argparse
import fnmatch
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path


OWNED_FOR_BASELINE = {"template", "merge"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", required=True, dest="applied_ref")
    parser.add_argument("--sha", required=True, dest="applied_sha")
    parser.add_argument("--manifest", default=".cerebro/upgrade-manifest.json")
    parser.add_argument("--output", default=".cerebro/upgrade-state.json")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"manifest not found: {manifest_path}")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes = collect_hashes(manifest)
    state = {
        "version": 1,
        "applied_ref": args.applied_ref,
        "applied_sha": args.applied_sha,
        "applied_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "hashes": hashes,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=output.parent,
        prefix=output.stem + ".",
        suffix=".tmp",
        delete=False,
    ) as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")
        tmp_path = Path(handle.name)
    tmp_path.replace(output)
    print(f"wrote {output} with {len(hashes)} file hash(es)")
    return 0


def collect_hashes(manifest: dict) -> dict[str, str]:
    paths = set()
    for entry in manifest.get("entries", []):
        if entry.get("ownership") not in OWNED_FOR_BASELINE:
            continue
        pattern = entry.get("path")
        if not pattern:
            continue
        paths.update(expand_pattern(pattern))

    return {path: sha256(Path(path)) for path in sorted(paths) if Path(path).is_file()}


def expand_pattern(pattern: str) -> set[str]:
    if not _has_glob(pattern):
        return {pattern} if Path(pattern).is_file() else set()
    return {
        str(path)
        for path in Path(".").rglob("*")
        if path.is_file() and fnmatch.fnmatch(str(path).removeprefix("./"), pattern)
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _has_glob(pattern: str) -> bool:
    return any(char in pattern for char in "*?[")


if __name__ == "__main__":
    raise SystemExit(main())
