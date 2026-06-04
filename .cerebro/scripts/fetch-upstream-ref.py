#!/usr/bin/env python3
"""Fetch a Cerebro upstream ref into the local upgrade cache and print its SHA."""

import argparse
import re
import subprocess
from pathlib import Path


REF_RE = re.compile(r"^[A-Za-z0-9._/-]+$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ref")
    parser.add_argument("--upstream", default="https://github.com/yelaco/claude-xmen.git")
    args = parser.parse_args()

    if args.ref in {"HEAD", "main", "master"}:
        print("ref must be an explicit tag or commit SHA, not HEAD/main/master")
        return 1
    if not REF_RE.match(args.ref):
        print(f"ref contains unsupported characters: {args.ref!r}")
        return 1

    cache_dir = Path(".cerebro/upgrade-cache") / args.ref
    try:
        if cache_dir.is_dir():
            subprocess.run(
                ["git", "-C", str(cache_dir), "fetch", "--depth=1", "origin", "tag", args.ref],
                check=True,
            )
            subprocess.run(["git", "-C", str(cache_dir), "checkout", args.ref], check=True)
        else:
            cache_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--filter=blob:none",
                    "--depth=1",
                    "--branch",
                    args.ref,
                    args.upstream,
                    str(cache_dir),
                ],
                check=True,
            )
        result = subprocess.run(
            ["git", "-C", str(cache_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("git is required for /cerebro-upgrade - install git and retry")
        return 1
    except subprocess.CalledProcessError:
        print(f"Could not fetch ref {args.ref!r} from {args.upstream}")
        return 1

    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
