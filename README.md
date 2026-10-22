# Above Base Camp

An interactive prototype atlas for Himalayan expeditions.

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
