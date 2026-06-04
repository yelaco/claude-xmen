#!/usr/bin/env python3
"""Resolve the latest version tag from the Cerebro upstream repository."""

import argparse
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", default="https://github.com/yelaco/claude-xmen.git")
    args = parser.parse_args()

    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--sort=-version:refname", args.upstream, "refs/tags/v*"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        print(f"Could not resolve latest upstream tag from {args.upstream}: {exc}")
        return 1

    for line in result.stdout.splitlines():
        if "refs/tags/" in line:
            print(line.rsplit("refs/tags/", 1)[1].removesuffix("^{}"))
            return 0

    print(f"Could not resolve latest upstream tag from {args.upstream}: no v* tags found")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
