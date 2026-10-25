#!/usr/bin/env python3
"""Build the dbt project, export site data, and serve the explorer."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORT = os.environ.get("PORT", "4173")


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> None:
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = str(ROOT)

    run(["dbt", "build"], env=env)
    run([sys.executable, "scripts/export_site_data.py"])

    print(f"Serving http://127.0.0.1:{PORT}  (Ctrl-C to stop)", flush=True)
    run([sys.executable, "-m", "http.server", PORT, "--directory", "dist"])


if __name__ == "__main__":
    main()
