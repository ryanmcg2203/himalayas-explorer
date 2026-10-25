"""Himalayas Explorer MCP server.

Expose the tested DuckDB marts as focused tools for natural-language agents.
Run with: python mcp_server.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
from mcp.server.mcpserver import MCPServer


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "above_base_camp.duckdb"
mcp = MCPServer("Himalayas Explorer")

SUCCESS_COLUMNS = {
    "recorded": "has_recorded_summit",
    "member": "has_member_summit",
    "undisputed": "has_undisputed_summit",
}
DENOMINATORS = {
    "team_member": {
        "column": "team",
        "death_column": "member_deaths",
        "label": "non-hired member attempts",
    },
    "summiter": {
        "column": "summiters",
        "death_column": "deaths",
        "label": "recorded summiters",
    },
    "expedition": {
        "column": "1",
        "death_column": "deaths",
        "label": "expedition rows",
    },
}


def query(sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
    if not DB_PATH.exists():
        raise RuntimeError(
            f"DuckDB database not found at {DB_PATH}. Run dbt build and "
            "scripts/export_site_data.py first."
        )
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        result = conn.execute(sql, params or [])
        columns = [column[0] for column in result.description]
        return [dict(zip(columns, values)) for values in result.fetchall()]
    finally:
        conn.close()


def like_pattern(value: str) -> str:
    """Build a literal substring LIKE pattern, not a wildcard expression."""
    escaped = value.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def text_result(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str, indent=2)


@mcp.tool()
def search_expeditions(
    query_text: str = "",
    peak: str = "",
    year_from: int = 0,
    year_to: int = 9999,
    limit: int = 20,
) -> str:
    """Find expedition records by peak, leader, route, nation, or year."""
    limit = max(1, min(limit, 100))
    needle = like_pattern(query_text)
    rows = query(
        """
        select id, year, mountain, leader_name, leader_or_role, leader_kind,
               nation, route, result, label, team, summiters, deaths,
               member_deaths, oxygen, disputed
        from mart_expeditions
        where year between ? and ?
          and (? = '' or lower(mountain) = lower(?))
          and (? = '' or lower(concat_ws(' ', mountain, leader_name, leader_or_role, nation, route, id)) like ? escape '\\')
        order by year desc, mountain
        limit ?
        """,
        [year_from, year_to, peak, peak, query_text, needle, limit],
    )
    return text_result({"count": len(rows), "records": rows})


@mcp.tool()
def search_climbers(query_text: str, limit: int = 20) -> str:
    """Find heuristic climber profiles by name, citizenship, or peak history."""
    limit = max(1, min(limit, 100))
    needle = f"%{query_text.lower()}%"
    rows = query(
        """
        select person_key, display_name, citizenship, expedition_appearances,
               identity_method
        from dim_person
        where lower(concat_ws(' ', display_name, citizenship)) like ?
        order by expedition_appearances desc, display_name
        limit ?
        """,
        [needle, limit],
    )
    return text_result({"count": len(rows), "profiles": rows})


@mcp.tool()
def get_expedition(expedition_id: str) -> str:
    """Retrieve one expedition record together with its member roster."""
    expedition = query("select * from mart_expeditions where id = ?", [expedition_id])
    members = query(
        """
        select person_key, full_name as display_name, year_of_birth, citizenship, status,
               age, is_leader, is_hired, summit_success, summit_disputed,
               died, death_height_m, oxygen_used
        from fct_expedition_member
        where expedition_id = ?
        order by is_leader desc, display_name
        """,
        [expedition_id],
    )
    return text_result({"expedition": expedition[0] if expedition else None, "members": members})


@mcp.tool()
def get_climber(person_key: str) -> str:
    """Retrieve one climber profile and their expedition-by-expedition history."""
    profile = query("select * from dim_person where person_key = ?", [person_key])
    activity = query(
        """
        select expedition_id, year, mountain, status, citizenship, age,
               is_leader, is_hired, summit_success, summit_disputed, died,
               death_height_m, oxygen_used
        from fct_expedition_member
        where person_key = ?
        order by year, expedition_id
        """,
        [person_key],
    )
    return text_result({"profile": profile[0] if profile else None, "activity": activity})


@mcp.tool()
def compare_peaks(
    peaks: list[str],
    year_from: int = 0,
    year_to: int = 9999,
    success_definition: str = "recorded",
    denominator: str = "team_member",
) -> str:
    """Compare selected peaks with explicit success and rate definitions."""
    if not peaks:
        return text_result({"error": "Provide at least one peak name."})
    if len(peaks) > 50:
        return text_result({"error": "Provide no more than 50 peak names at a time."})
    peaks = list(dict.fromkeys(peak.strip() for peak in peaks if peak.strip()))
    if not peaks:
        return text_result({"error": "Provide at least one non-empty peak name."})
    if success_definition not in {"recorded", "member", "undisputed"}:
        return text_result({"error": "success_definition must be recorded, member, or undisputed."})
    if denominator not in {"team_member", "summiter", "expedition"}:
        return text_result({"error": "denominator must be team_member, summiter, or expedition."})
    success_column = {"recorded": "has_recorded_summit", "member": "has_member_summit", "undisputed": "has_undisputed_summit"}[success_definition]
    denominator_spec = DENOMINATORS[denominator]
    base_column = denominator_spec["column"]
    death_column = denominator_spec["death_column"]
    placeholders = ",".join("?" for _ in peaks)
    rows = query(
        f"""
        select mountain, count(*) as expeditions,
               sum(case when {success_column} then 1 else 0 end) as successes,
               round(100.0 * sum(case when {success_column} then 1 else 0 end) / nullif(count(*), 0), 2) as success_rate_pct,
               sum({death_column}) as deaths,
               sum({base_column}) as denominator_total,
               round(100.0 * sum({death_column}) / nullif(sum({base_column}), 0), 2) as deaths_per_100_denominator
        from mart_expeditions
        where year between ? and ? and mountain in ({placeholders})
        group by mountain order by deaths_per_100_denominator desc
        """,
        [year_from, year_to, *peaks],
    )
    return text_result({
        "success_definition": success_definition,
        "denominator": denominator,
        "success_rate_definition": "successful expeditions / expedition rows",
        "death_rate_definition": f"{denominator_spec['death_column']} / {denominator_spec['label']} × 100",
        "results": rows,
    })


@mcp.tool()
def compare_eras(
    year_from: int = 0,
    year_to: int = 9999,
    success_definition: str = "recorded",
    denominator: str = "team_member",
) -> str:
    """Compare early, expeditionary, transitional, and commercial periods."""
    if success_definition not in {"recorded", "member", "undisputed"}:
        return text_result({"error": "success_definition must be recorded, member, or undisputed."})
    if denominator not in {"team_member", "summiter", "expedition"}:
        return text_result({"error": "denominator must be team_member, summiter, or expedition."})
    success_column = {
        "recorded": "has_recorded_summit",
        "member": "has_member_summit",
        "undisputed": "has_undisputed_summit",
    }[success_definition]
    denominator_spec = DENOMINATORS[denominator]
    base_column = denominator_spec["column"]
    death_column = denominator_spec["death_column"]
    rows = query(
        f"""
        with classified as (
            select *
            from mart_expeditions
            where year between ? and ?
        )
        select era, min(year) as first_year, max(year) as last_year,
               count(*) as expeditions,
               sum(case when {success_column} then 1 else 0 end) as successes,
               round(100.0 * sum(case when {success_column} then 1 else 0 end) / nullif(count(*), 0), 2) as success_rate_pct,
               sum({death_column}) as deaths,
               sum({base_column}) as denominator_total,
               round(100.0 * sum({death_column}) / nullif(sum({base_column}), 0), 2) as deaths_per_100_denominator
        from classified
        group by era
        order by first_year
        """,
        [year_from, year_to],
    )
    return text_result({
        "success_definition": success_definition,
        "denominator": denominator,
        "success_rate_definition": "successful expeditions / expedition rows",
        "death_rate_definition": f"{denominator_spec['death_column']} / {denominator_spec['label']} × 100",
        "results": rows,
    })


@mcp.tool()
def explain_metric(metric: str) -> str:
    """Explain a metric's grain, denominator, and known caveats."""
    definitions = {
        "recorded_success": "An expedition has at least one recorded summiter. Grain: expedition.",
        "member_success": "An expedition has at least one recorded non-hired member summiter. Grain: expedition.",
        "undisputed_success": "An expedition has a recorded summit and is not marked disputed. Grain: expedition.",
        "death_rate": "The selected death numerator divided by the selected denominator, reported as deaths per 100 denominator units. Team-member rates use member_deaths; summiter and expedition rates use recorded deaths.",
        "person_identity": "A heuristic grouping of normalized name, year of birth, and citizenship; aliases and collisions remain possible. Profiles are classified low, moderate, or review confidence.",
    }
    return text_result({"metric": metric, "explanation": definitions.get(metric, "Unknown metric. Try recorded_success, member_success, undisputed_success, death_rate, or person_identity.")})


if __name__ == "__main__":
    mcp.run()
