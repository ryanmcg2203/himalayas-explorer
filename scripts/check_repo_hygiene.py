#!/usr/bin/env python3
"""Fail if tracked files would accidentally redistribute local data."""
from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath


ALLOWED_DATA = {"data/README.md"}
ALLOWED_DIST_SUFFIXES = {".html"}
BLOCKED_SUFFIXES = {
    ".csv", ".csv.gz", ".dbf", ".duckdb", ".gz", ".json", ".ndjson",
    ".parquet", ".zip",
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True
    )
    return result.stdout.decode().split("\0")[:-1]


def main() -> int:
    violations: list[str] = []
    for filename in tracked_files():
        path = PurePosixPath(filename)
        suffix = "".join(path.suffixes).lower()
        if filename.startswith("data/") and filename not in ALLOWED_DATA:
            violations.append(filename)
        if filename.startswith("dist/") and path.suffix.lower() not in ALLOWED_DIST_SUFFIXES:
            violations.append(filename)
        if suffix in BLOCKED_SUFFIXES:
            violations.append(filename)
    if violations:
        print("Unexpected tracked data-like files:", file=sys.stderr)
        for filename in sorted(set(violations)):
            print(f"  {filename}", file=sys.stderr)
        return 1
    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
