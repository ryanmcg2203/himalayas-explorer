#!/usr/bin/env python3
"""Export the dbt expedition mart to the static site's JSON contract."""
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "above_base_camp.duckdb"
OUT = ROOT / "dist" / "expeditions.json"
PEAKS_INPUT = ROOT / "data" / "bronze" / "peaks.json"
PEAKS_OUT = ROOT / "dist" / "peaks.json"
PEOPLE_OUT = ROOT / "dist" / "people.json"
ACTIVITY_OUT = ROOT / "dist" / "person_activity.json"
MEMBERS_OUT = ROOT / "dist" / "expedition_members.json"


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
        row["leaderOrRole"] = row.pop("leader_or_role")
        row["leaderKind"] = row.pop("leader_kind")
        row["leaderName"] = row.pop("leader_name")
        row["sourceResult"] = row["result"]
        row["sourceLabel"] = row["label"]
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(rows):,} rows to {OUT}")

    if not PEAKS_INPUT.exists():
        raise SystemExit(f"Missing {PEAKS_INPUT}; run scripts/build_data.py first")
    PEAKS_OUT.write_bytes(PEAKS_INPUT.read_bytes())
    print(f"Exported peak metadata to {PEAKS_OUT}")

    conn = duckdb.connect(str(DB), read_only=True)
    result = conn.execute("""
        select f.person_key, f.full_name, f.citizenship, f.year, f.mountain,
               f.summit_success, f.died, f.is_hired,
               d.identity_confidence, d.identity_method
        from fct_expedition_member f
        join dim_person d using (person_key)
        where full_name <> ''
        order by person_key, year
    """)
    columns = [column[0] for column in result.description]
    people = {}
    for values in result.fetchall():
        row = dict(zip(columns, values))
        key = row["person_key"]
        person = people.setdefault(key, {
            "personKey": key,
            "name": row["full_name"],
            "citizenship": row["citizenship"],
            "identityConfidence": row["identity_confidence"],
            "identityMethod": row["identity_method"],
            "appearances": 0,
            "summits": 0,
            "deaths": 0,
            "hiredAppearances": 0,
            "peaks": set(),
            "years": set(),
        })
        person["appearances"] += 1
        person["summits"] += int(row["summit_success"])
        person["deaths"] += int(row["died"])
        person["hiredAppearances"] += int(row["is_hired"])
        person["peaks"].add(row["mountain"])
        person["years"].add(row["year"])
    conn.close()
    people_rows = []
    for person in people.values():
        person["peaks"] = sorted(person["peaks"])
        person["years"] = sorted(person["years"])
        people_rows.append(person)
    people_rows.sort(key=lambda item: (-item["appearances"], item["name"]))
    PEOPLE_OUT.write_text(json.dumps(people_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(people_rows):,} people to {PEOPLE_OUT}")

    conn = duckdb.connect(str(DB), read_only=True)
    activity = conn.execute("""
        select person_key, expedition_id, year, mountain, status,
               is_hired, summit_success, died
        from fct_expedition_member
        where full_name <> ''
        order by person_key, year
    """).fetchall()
    conn.close()
    activity_rows = [{
        "personKey": row[0], "expeditionId": row[1], "year": row[2],
        "mountain": row[3], "status": row[4], "hired": row[5],
        "summit": row[6], "died": row[7],
    } for row in activity]
    ACTIVITY_OUT.write_text(json.dumps(activity_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(activity_rows):,} activity rows to {ACTIVITY_OUT}")

    conn = duckdb.connect(str(DB), read_only=True)
    result = conn.execute("""
        select expedition_id, person_key, full_name, first_name, last_name,
               citizenship, age, status, occupation, is_leader, is_support,
               is_hired, is_sherpa, summit_success, summit_claimed,
               summit_disputed, reached_high_point, oxygen_used, died,
               death_date, death_type, death_height_m, death_class,
               had_ams, weather_related, injured
        from fct_expedition_member
        where full_name <> ''
        order by expedition_id, is_hired, full_name
    """)
    columns = [column[0] for column in result.description]
    member_rows = []
    for values in result.fetchall():
        row = dict(zip(columns, values))
        member_rows.append({
            "expeditionId": row["expedition_id"], "personKey": row["person_key"],
            "name": row["full_name"], "firstName": row["first_name"],
            "lastName": row["last_name"], "citizenship": row["citizenship"],
            "age": row["age"], "status": row["status"], "occupation": row["occupation"],
            "leader": row["is_leader"], "support": row["is_support"],
            "hired": row["is_hired"], "sherpa": row["is_sherpa"],
            "summit": row["summit_success"], "claimed": row["summit_claimed"],
            "disputed": row["summit_disputed"], "highPoint": row["reached_high_point"],
            "oxygen": row["oxygen_used"], "died": row["died"],
            "deathDate": row["death_date"], "deathType": row["death_type"],
            "deathHeight": row["death_height_m"], "deathClass": row["death_class"],
            "ams": row["had_ams"], "weather": row["weather_related"],
            "injured": row["injured"],
        })
    conn.close()
    MEMBERS_OUT.write_text(json.dumps(member_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(member_rows):,} expedition members to {MEMBERS_OUT}")


if __name__ == "__main__":
    main()
