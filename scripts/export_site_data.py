#!/usr/bin/env python3
"""Export the dbt expedition mart to the static site's JSON contract."""
import json
import os
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "above_base_camp.duckdb"
FREDDY_KEY = "easter-egg-freddy-t-bear"
OUT = ROOT / "dist" / "expeditions.json"
PEAKS_INPUT = ROOT / "data" / "bronze" / "peaks.json"
PEAKS_OUT = ROOT / "dist" / "peaks.json"
PEOPLE_OUT = ROOT / "dist" / "people.json"
MEMBERS_OUT = ROOT / "dist" / "expedition_members.json"
ACTIVITY_OUT = ROOT / "dist" / "person_activity.json"
META_OUT = ROOT / "dist" / "site_meta.json"
REQUIRED_MART_FIELDS = {
    "id", "year", "mountain", "peak_id", "team", "hired", "participants",
    "summiters", "summit_hired", "member_summiters", "deaths", "member_deaths",
    "hired_deaths", "season", "disputed", "route", "route2", "route3", "route4",
    "route_normalized", "route2_normalized", "route3_normalized", "route4_normalized",
}
BOOLEAN_FIELDS = {
    "disputed", "claimed", "has_recorded_summit", "has_member_summit",
    "has_undisputed_summit",
}
EXPORT_SCHEMAS = {
    "peak export": {
        "peakId", "name", "heightM", "expeditions", "memberAttempts",
        "memberSummits", "memberDeaths", "hiredDeaths", "deaths",
        "memberSummitRate", "decadeCounts",
    },
    "people export": {
        "personKey", "name", "citizenship", "identityConfidence", "identityMethod",
        "appearances", "summits", "deaths", "hiredAppearances", "peaks", "years",
        "birthYear", "identityReason", "possibleMerge", "firstYear", "lastYear",
        "topPeakId", "topPeak",
    },
    "member export": {
        "expeditionId", "personKey", "year", "mountain", "name", "citizenship",
        "age", "status", "occupation", "leader", "support", "hired", "sherpa",
        "summit", "claimed", "disputed", "highPoint", "oxygen", "died", "deathDate",
        "deathType", "deathHeight", "deathClass", "ams", "weather", "injured",
    },
    "activity export": {
        "personKey", "expeditionId", "year", "mountain", "status", "hired", "summit", "died",
    },
}


def as_bool(value):
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "y", "yes"}
    return bool(value) if value is not None else False


def as_optional_bool(value):
    if value is None or value == "":
        return None
    if isinstance(value, str) and value.strip().lower() in {"no", "n", "0", "false"}:
        return False
    return as_bool(value)


def validate_export(rows, label):
    required = EXPORT_SCHEMAS[label]
    for index, row in enumerate(rows):
        missing = sorted(required.difference(row))
        if missing:
            raise SystemExit(f"{label} row {index} is missing fields: {', '.join(missing)}")
    return rows


def main() -> None:
    if os.environ.get("HIMALAYAS_LOCAL_ONLY") != "1":
        raise SystemExit(
            "Refusing to export database-derived site data without "
            "HIMALAYAS_LOCAL_ONLY=1"
        )
    conn = duckdb.connect(str(DB), read_only=True)
    result = conn.execute("select * from mart_expeditions order by year, id")
    columns = [column[0] for column in result.description]
    missing = REQUIRED_MART_FIELDS.difference(columns)
    if missing:
        raise SystemExit(f"mart_expeditions is missing required fields: {', '.join(sorted(missing))}")
    rows = [dict(zip(columns, values)) for values in result.fetchall()]
    conn.close()
    for row in rows:
        for key, value in row.items():
            if hasattr(value, "item"):
                row[key] = value.item()
        row["sourceId"] = row.pop("source_id")
        row["peakId"] = row.pop("peak_id")
        row["teamMembers"] = row.pop("team")
        row["hiredStaff"] = row.pop("hired")
        row["summitHired"] = row.pop("summit_hired")
        row["memberSummiters"] = row.pop("member_summiters")
        row["memberDeaths"] = row.pop("member_deaths")
        row["hiredDeaths"] = row.pop("hired_deaths")
        row["routeNormalized"] = row.pop("route_normalized")
        row["route2Normalized"] = row.pop("route2_normalized")
        row["route3Normalized"] = row.pop("route3_normalized")
        row["route4Normalized"] = row.pop("route4_normalized")
        row["leaderOrRole"] = row.pop("leader_or_role")
        row["leaderKind"] = row.pop("leader_kind")
        row["leaderName"] = row.pop("leader_name")
        row["sourceResult"] = row["result"]
        row["sourceLabel"] = row["label"]
        row["oxygen"] = as_optional_bool(row["oxygen"])
        row["hasRecordedSummit"] = as_bool(row.pop("has_recorded_summit"))
        row["hasMemberSummit"] = as_bool(row.pop("has_member_summit"))
        row["hasUndisputedSummit"] = as_bool(row.pop("has_undisputed_summit"))
        for field in BOOLEAN_FIELDS.intersection(row):
            row[field] = as_bool(row[field])
    conn = duckdb.connect(str(DB), read_only=True)
    roster_counts = conn.execute("""
        select expedition_id,
               count(*) as roster_rows,
               sum(case when not is_hired then 1 else 0 end) as roster_member_rows,
               sum(case when is_hired then 1 else 0 end) as roster_hired_rows,
               sum(case when not is_hired and summit_success then 1 else 0 end) as roster_member_summits,
               sum(case when is_hired and summit_success then 1 else 0 end) as roster_hired_summits,
               sum(case when not is_hired and died then 1 else 0 end) as roster_member_deaths,
               sum(case when is_hired and died then 1 else 0 end) as roster_hired_deaths,
               sum(case when summit_disputed then 1 else 0 end) as roster_disputed_summits,
               sum(case when summit_claimed then 1 else 0 end) as roster_claimed_summits
        from fct_expedition_member
        where full_name <> ''
        group by expedition_id
    """).fetchall()
    conn.close()
    rows_by_id = {row["id"]: row for row in rows}
    roster_fields = (
        "rosterRows", "rosterMemberRows", "rosterHiredRows", "rosterMemberSummits",
        "rosterHiredSummits", "rosterMemberDeaths", "rosterHiredDeaths",
        "rosterDisputedSummits", "rosterClaimedSummits",
    )
    for row in rows:
        row.update({field: 0 for field in roster_fields})
    for values in roster_counts:
        key = values[0]
        if key not in rows_by_id:
            continue
        rows_by_id[key].update({
            "rosterRows": int(values[1]), "rosterMemberRows": int(values[2]),
            "rosterHiredRows": int(values[3]), "rosterMemberSummits": int(values[4]),
            "rosterHiredSummits": int(values[5]), "rosterMemberDeaths": int(values[6]),
            "rosterHiredDeaths": int(values[7]), "rosterDisputedSummits": int(values[8]),
            "rosterClaimedSummits": int(values[9]),
        })
    OUT.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(rows):,} rows to {OUT}")

    if not PEAKS_INPUT.exists():
        raise SystemExit(f"Missing {PEAKS_INPUT}; run scripts/build_data.py first")
    conn = duckdb.connect(str(DB), read_only=True)
    result = conn.execute("select * from mart_peaks order by name")
    columns = [column[0] for column in result.description]
    peak_rows = []
    for values in result.fetchall():
        row = dict(zip(columns, values))
        for key, value in row.items():
            if hasattr(value, "item"):
                row[key] = value.item()
        row["peakId"] = row.pop("peak_id")
        row["memberAttempts"] = row.pop("member_attempts")
        row["memberSummits"] = row.pop("member_summits")
        row["memberDeaths"] = row.pop("member_deaths")
        row["hiredDeaths"] = row.pop("hired_deaths")
        row["memberSummitRate"] = row.pop("member_summit_rate")
        raw_decades = json.loads(row.pop("decade_counts"))
        row["decadeCounts"] = {str(int(float(key))): value for key, value in raw_decades.items()}
        peak_rows.append(row)
    conn.close()
    validate_export(peak_rows, "peak export")
    PEAKS_OUT.write_text(json.dumps(peak_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
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
    conn = duckdb.connect(str(DB), read_only=True)
    profile_rows = conn.execute("""
        select person_key, year_of_birth, identity_reason, possible_merge,
               first_year, last_year, top_peak_id, top_peak, peaks, years
        from mart_person_profile
    """).fetchall()
    conn.close()
    people_by_key = {person["personKey"]: person for person in people_rows}
    for values in profile_rows:
        key, birth_year, reason, possible_merge, first_year, last_year, top_peak_id, top_peak, peaks_json, years_json = values
        person = people_by_key.get(key)
        if not person:
            continue
        person.update({
            "birthYear": birth_year,
            "identityReason": reason,
            "possibleMerge": bool(possible_merge),
            "firstYear": first_year,
            "lastYear": last_year,
            "topPeakId": top_peak_id,
            "topPeak": top_peak,
            "peaks": json.loads(peaks_json),
            "years": json.loads(years_json),
        })
    people_rows.append({
        "personKey": FREDDY_KEY,
        "name": "Freddy T. Bear",
        "citizenship": "Ireland",
        "identityConfidence": "easter egg",
        "identityMethod": "curated site character",
        "appearances": 1,
        "summits": 0,
        "deaths": 0,
        "hiredAppearances": 0,
        "peaks": ["Everest"],
        "years": [2004],
        "birthYear": None,
        "identityReason": "Curated educational expedition companion entry",
        "possibleMerge": False,
        "firstYear": 2004,
        "lastYear": 2004,
        "topPeakId": "EVER",
        "topPeak": "Everest",
        "easterEgg": True,
    })
    people_rows.sort(key=lambda item: (-item["appearances"], item["name"]))
    validate_export(people_rows, "people export")
    PEOPLE_OUT.write_text(json.dumps(people_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(people_rows):,} people to {PEOPLE_OUT}")

    conn = duckdb.connect(str(DB), read_only=True)
    result = conn.execute("""
        select expedition_id, person_key, year, mountain, full_name, first_name, last_name,
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
            "year": row["year"], "mountain": row["mountain"],
            "name": row["full_name"], "firstName": row["first_name"],
            "lastName": row["last_name"], "citizenship": row["citizenship"],
            "age": row["age"], "status": row["status"], "occupation": row["occupation"],
            "leader": as_bool(row["is_leader"]), "support": as_bool(row["is_support"]),
            "hired": as_bool(row["is_hired"]), "sherpa": as_bool(row["is_sherpa"]),
            "summit": as_bool(row["summit_success"]), "claimed": as_bool(row["summit_claimed"]),
            "disputed": as_bool(row["summit_disputed"]), "highPoint": as_bool(row["reached_high_point"]),
            "oxygen": None if row["oxygen_used"] is None else as_bool(row["oxygen_used"]),
            "died": as_bool(row["died"]),
            "deathDate": row["death_date"], "deathType": row["death_type"],
            "deathHeight": row["death_height_m"], "deathClass": row["death_class"],
            "ams": as_bool(row["had_ams"]), "weather": as_bool(row["weather_related"]),
            "injured": as_bool(row["injured"]),
        })
    conn.close()
    member_rows.append({
        "expeditionId": "2004-EVER04148", "personKey": FREDDY_KEY,
        "year": 2004, "mountain": "Everest", "name": "Freddy T. Bear",
        "firstName": "Freddy T.", "lastName": "Bear", "citizenship": "Ireland",
        "age": None, "status": "Educational companion", "occupation": "Expedition mascot",
        "leader": False, "support": True, "hired": False, "sherpa": False,
        "summit": False, "claimed": False, "disputed": False, "highPoint": False,
        "oxygen": True, "died": False, "deathDate": "", "deathType": 0,
        "deathHeight": 0, "deathClass": 0, "ams": False, "weather": False,
        "injured": False, "easterEgg": True,
    })
    activity_rows = [
        {
            "personKey": row["personKey"],
            "expeditionId": row["expeditionId"],
            "year": row["year"],
            "mountain": row["mountain"],
            "status": row["status"],
            "hired": row["hired"],
            "summit": row["summit"],
            "died": row["died"],
        }
        for row in member_rows
    ]
    validate_export(member_rows, "member export")
    validate_export(activity_rows, "activity export")
    MEMBERS_OUT.write_text(json.dumps(member_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(member_rows):,} expedition members to {MEMBERS_OUT}")
    ACTIVITY_OUT.write_text(json.dumps(activity_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(activity_rows):,} compact person activity rows to {ACTIVITY_OUT}")

    peak_count = len(json.loads(PEAKS_INPUT.read_text(encoding="utf-8")))
    years = [row["year"] for row in rows]
    META_OUT.write_text(json.dumps({
        "peakCount": peak_count,
        "expeditionCount": len(rows),
        "coverageStart": min(years) if years else None,
        "coverageEnd": max(years) if years else None,
        "memberRowCount": sum(1 for row in member_rows if not row.get("easterEgg")),
    }, separators=(",", ":")), encoding="utf-8")
    print(f"Exported site metadata to {META_OUT}")


if __name__ == "__main__":
    main()
