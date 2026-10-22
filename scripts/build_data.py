#!/usr/bin/env python3
r"""Build a compact, app-friendly expedition index from the official HDB zip.

Usage:
  python3 scripts/build_data.py /path/to/Himalayan\ Database.zip

The raw database is intentionally not copied into the repository. The output
contains only fields used by the interactive atlas.
"""
from __future__ import annotations

import json
import gzip
import sys
import tempfile
import zipfile
from pathlib import Path

from dbfread import DBF


def unpack_table(archive: zipfile.ZipFile, filename: str, destination: Path) -> Path:
    member = next(name for name in archive.namelist() if name.lower().endswith(f"/himdata/{filename.lower()}.dbf"))
    memo = next((name for name in archive.namelist() if name.lower().endswith(f"/himdata/{filename.lower()}.fpt")), None)
    archive.extract(member, destination)
    if memo:
        archive.extract(memo, destination)
    return destination / member


def clean(value):
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/build_data.py /path/to/Himalayan Database.zip")
    archive_path = Path(sys.argv[1]).expanduser()
    if not archive_path.exists():
        raise SystemExit(f"Archive not found: {archive_path}")

    output = Path(__file__).resolve().parents[1] / "data" / "bronze" / "expeditions.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="hdb-") as temp:
        temp_path = Path(temp)
        with zipfile.ZipFile(archive_path) as archive:
            exped_path = unpack_table(archive, "exped", temp_path)
            members_path = unpack_table(archive, "members", temp_path)
            peaks_path = unpack_table(archive, "peaks", temp_path)
            exped = list(DBF(str(exped_path), load=False, char_decode_errors="ignore"))
            members = list(DBF(str(members_path), load=False, char_decode_errors="ignore"))
            peaks = DBF(str(peaks_path), load=True, char_decode_errors="ignore")

        peak_names = {row["PEAKID"]: clean(row["PKNAME"]).strip() for row in peaks}
        records = []
        for row in exped:
            year = str(clean(row["YEAR"])).strip()
            if not year.isdigit():
                continue
            success = any(bool(row.get(f"SUCCESS{i}")) for i in range(1, 5))
            deaths = int(row.get("MDEATHS") or 0) + int(row.get("HDEATHS") or 0)
            if success:
                result, label = "summit", "Summit"
            elif deaths:
                result, label = "fail", "Tragedy"
            else:
                result, label = "mixed", "Turned back"

            route = clean(row.get("ROUTE1")).strip()
            style = "Commercial" if bool(row.get("COMRTE")) else ("Alpine" if bool(row.get("STDRTE")) else "Siege")
            records.append({
                "id": f"{year}-{clean(row['EXPID']).strip()}",
                "sourceId": clean(row["EXPID"]).strip(),
                "year": int(year),
                "mountain": peak_names.get(row["PEAKID"], row["PEAKID"]),
                "peakId": clean(row["PEAKID"]).strip(),
                "team": int(row.get("TOTMEMBERS") or 0),
                "hired": int(row.get("TOTHIRED") or 0),
                "summiters": int(row.get("SMTMEMBERS") or 0),
                "summitHired": int(row.get("SMTHIRED") or 0),
                "deaths": deaths,
                "result": result,
                "label": label,
                "style": style,
                "oxygen": "Yes" if bool(row.get("O2USED")) else "No",
                "leader": clean(row.get("LEADERS")).strip(),
                "nation": clean(row.get("NATION")).strip(),
                "route": route,
                "season": int(row.get("SEASON") or 0),
                "disputed": bool(row.get("DISPUTED")),
                "claimed": bool(row.get("CLAIMED")),
            })

    records.sort(key=lambda item: (item["year"], item["id"]))
    output.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    member_records = []
    for row in members:
        year = str(clean(row.get("MYEAR"))).strip()
        source_expid = clean(row.get("EXPID")).strip()
        member_id = clean(row.get("MEMBID")).strip()
        if not year.isdigit() or not source_expid or not member_id:
            continue
        member_records.append({
            "id": f"{year}-{source_expid}-{member_id}",
            "expeditionId": f"{year}-{source_expid}",
            "sourceExpid": source_expid,
            "memberId": member_id,
            "year": int(year),
            "peakId": clean(row.get("PEAKID")).strip(),
            "firstName": clean(row.get("FNAME")).strip(),
            "lastName": clean(row.get("LNAME")).strip(),
            "sex": clean(row.get("SEX")).strip(),
            "age": int(row.get("CALCAGE") or 0),
            "yob": clean(row.get("YOB")).strip(),
            "citizen": clean(row.get("CITIZEN")).strip(),
            "status": clean(row.get("STATUS")).strip(),
            "occupation": clean(row.get("OCCUPATION")).strip(),
            "leader": bool(row.get("LEADER")),
            "support": bool(row.get("SUPPORT")),
            "hired": bool(row.get("HIRED")),
            "sherpa": bool(row.get("SHERPA")),
            "tibetan": bool(row.get("TIBETAN")),
            "success": bool(row.get("MSUCCESS")),
            "claimed": bool(row.get("MCLAIMED")),
            "disputed": bool(row.get("MDISPUTED")),
            "highPoint": bool(row.get("MHIGHPT")),
            "oxygen": bool(row.get("MO2USED")),
            "death": bool(row.get("DEATH")),
            "deathDate": clean(row.get("DEATHDATE")),
            "deathType": int(row.get("DEATHTYPE") or 0),
            "deathHeight": int(row.get("DEATHHGTM") or 0),
            "deathClass": int(row.get("DEATHCLASS") or 0),
            "ams": bool(row.get("AMS")),
            "weather": bool(row.get("WEATHER")),
            "injury": bool(row.get("INJURY")),
        })
    member_output = output.parent / "members.json.gz"
    with gzip.open(member_output, "wt", encoding="utf-8") as stream:
        json.dump(member_records, stream, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {len(records):,} expeditions to {output} ({output.stat().st_size / 1_000_000:.1f} MB)")
    print(f"Wrote {len(member_records):,} members to {member_output} ({member_output.stat().st_size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
