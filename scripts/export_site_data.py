#!/usr/bin/env python3
"""Export the dbt expedition mart to the static site's JSON contract."""
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "above_base_camp.duckdb"
OUT = ROOT / "dist" / "expeditions.json"


def main() -> None:
    conn = duckdb.connect(str(DB), read_only=True)
    result = conn.execute("select * from mart_expeditions order by year, id")
    columns = [column[0] for column in result.description]
    rows = [dict(zip(columns, values)) for values in result.fetchall()]
    conn.close()
    for row in rows:
        for key, value in row.items():
            if hasattr(value, "item"):
                row[key] = value.item()
        row["sourceId"] = row.pop("source_id")
        row["peakId"] = row.pop("peak_id")
        row["summitHired"] = row.pop("summit_hired")
        row["sourceResult"] = row["result"]
        row["sourceLabel"] = row["label"]
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(rows):,} rows to {OUT}")


if __name__ == "__main__":
    main()
