#!/usr/bin/env python3
"""Fail if tracked files would accidentally redistribute local data."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath


ALLOWED_DATA = {"data/README.md"}
ALLOWED_DIST_SUFFIXES = {".html", ".js"}
MAX_TRACKED_FILE_BYTES = 1_000_000
BLOCKED_SUFFIXES = {
    ".csv", ".csv.gz", ".dbf", ".duckdb", ".gz", ".json", ".ndjson",
    ".parquet", ".zip",
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True
    )
    return result.stdout.decode().split("\0")[:-1]


def historical_files() -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--objects", "--all"], check=True, capture_output=True
    )
    return [line.split(" ", 1)[1] for line in result.stdout.decode().splitlines() if " " in line]


def main() -> int:
    violations: list[str] = []
    current = tracked_files()
    for filename in current:
        path = PurePosixPath(filename)
        suffix = "".join(path.suffixes).lower()
        if filename.startswith("data/") and filename not in ALLOWED_DATA:
            violations.append(filename)
        if filename.startswith("dist/") and path.suffix.lower() not in ALLOWED_DIST_SUFFIXES:
            violations.append(filename)
        if suffix in BLOCKED_SUFFIXES:
            violations.append(filename)
        try:
            if Path(filename).stat().st_size > MAX_TRACKED_FILE_BYTES:
                violations.append(f"{filename} (larger than {MAX_TRACKED_FILE_BYTES} bytes)")
        except FileNotFoundError:
            violations.append(f"{filename} (tracked file is missing)")

    historical_violations = []
    for filename in historical_files():
        path = PurePosixPath(filename)
        suffix = "".join(path.suffixes).lower()
        if (filename.startswith("data/") and filename not in ALLOWED_DATA) or suffix in BLOCKED_SUFFIXES:
            historical_violations.append(filename)
    if historical_violations:
        violations.extend(f"{filename} (present in git history)" for filename in sorted(set(historical_violations)))
    if violations:
        print("Unexpected tracked data-like files:", file=sys.stderr)
        for filename in sorted(set(violations)):
            print(f"  {filename}", file=sys.stderr)
        return 1
    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
