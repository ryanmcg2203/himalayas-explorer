# Above Base Camp

An interactive atlas for Himalayan expeditions, risk, and changing definitions.

The site combines a responsive static explorer with a local DuckDB/dbt data
pipeline. It currently ships with 11,854 derived expedition records spanning
1905–2025 and 439 peaks.

## Explore

The interface supports peak, outcome, era, success-definition, and denominator
filters. It makes the metric choices visible: success can mean any recorded
summit, a member summit excluding hired staff, or an undisputed summit; rates
can be calculated per team member, summiter, or expedition.

## Run it

From this directory:

```bash
python3 -m http.server 4173 --directory dist
```

Then open <http://127.0.0.1:4173>.

The static site reads `dist/expeditions.json`. The reproducible source-to-mart pipeline is described below and preserves the UI's explicit outcome definitions.

## Rebuild the data layer

Create a project-local environment, install the Python tools, then run dbt and export the tested mart:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
DBT_PROFILES_DIR=. dbt build
python scripts/export_site_data.py
```

The dbt models live in `models/` and the semantic checks live in `tests/`. The DuckDB file is generated at `data/above_base_camp.duckdb` and is intentionally local.

The member layer adds 94,999 person-on-expedition records in
`fct_expedition_member` and a cautious, heuristic `dim_person`. Person
identity is grouped by normalized name, year of birth, and citizenship; it is
not presented as perfect identity resolution.

## Rebuild from the official database

Download the current database archive from the [Himalayan Database downloads
page](https://www.himalayandatabase.com/downloads.html), then build the compact
site index before running dbt:

```bash
python scripts/build_data.py "/path/to/Himalayan Database.zip"
DBT_PROFILES_DIR=. dbt build
python scripts/export_site_data.py
```

The raw archive is not checked in. The compact bronze input is stored at
`data/bronze/expeditions.json` and compressed `members.json.gz`; the importer creates stable IDs for source
IDs that collide across centuries, while preserving the original source ID.
