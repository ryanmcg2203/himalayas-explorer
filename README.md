# Himalayas Explorer

A local explorer for Himalayan expeditions, ascents, and deaths.

The site combines a responsive static explorer with a local DuckDB/dbt data
pipeline. The repository contains code and documentation only; generated
database and site data stay local because the Himalayan Database's terms
restrict redistribution.

## Explore

The interface supports peak, measure, and grouping controls. It makes the
metric choices visible: the chart can show expeditions, member summits,
success rate, or deaths, grouped by year, decade, season, oxygen use, or
member/hired-staff population.

## Quickstart

This is a local-only build. The repository does not contain the Himalayan
Database archive, the DuckDB database, or generated JSON exports. To use the
data pipeline, first obtain the current archive from the
[Himalayan Database downloads page](https://www.himalayandatabase.com/downloads.html),
then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_data.py "/path/to/Himalayan Database.zip"
DBT_PROFILES_DIR="$PWD" dbt build
HIMALAYAS_LOCAL_ONLY=1 python scripts/export_site_data.py
python -m http.server 4173 --directory dist
```

Open <http://127.0.0.1:4173>. The generated database and JSON exports stay
local and must not be uploaded to a public static host. The member layer and
provisional identity model are rebuilt from the same snapshot; do not treat a
profile as a confirmed real-world identity.

For the same workflow with one command after the initial import, use
`python scripts/run_site.py`.

If the local database and exports already exist and you only want to inspect
the frontend, run:

```bash
python scripts/build_site.py
python -m http.server 4173 --directory dist
```

Then open <http://127.0.0.1:4173>. Frontend edits belong in `src/`; the build
script copies them into the generated `dist/` directory.

The browser source lives in `src/`. Run `python scripts/build_site.py` after
editing it to rebuild the generated `dist/` frontend. If working from an older
checkout that predates the source tree, `python scripts/build_site.py
--bootstrap` extracts the existing checked-in pages into `src/` first.

## Data pipeline

The pipeline has four layers:

1. **Staging** — lightly cleans the imported expedition and member tables.
2. **Intermediate** — classifies expedition eras and constructs provisional
   identity groups for member records.
3. **Marts** — creates the tables used by the explorer, including expeditions,
   peaks, people, peak-year summaries, and member-level records.
4. **Export** — converts the local DuckDB marts into JSON files consumed by the
   static frontend.

The dbt project materializes staging and intermediate models as views and the
final marts as tables. Run `dbt build` to rebuild the models and execute the
data-quality tests.

The dbt models live in `models/` and the semantic checks live in `tests/`. The
raw archive, bronze extracts, DuckDB database, and static JSON exports are
ignored locally. The importer creates stable IDs for source IDs that collide
across centuries while preserving the original source ID.

### Inspecting the dbt project

After building the local database and models, generate and serve the dbt
documentation:

```bash
DBT_PROFILES_DIR="$PWD" dbt docs generate
DBT_PROFILES_DIR="$PWD" dbt docs serve --port 8081
```

Then open <http://127.0.0.1:8081>. The documentation includes the model
lineage graph, compiled SQL, model dependencies, and test results.

The main lineage is:

```text
Himalayan Database archive
          ↓
      DuckDB import
          ↓
       dbt staging
          ↓
     dbt intermediate
   identity + era logic
          ↓
       dbt marts
          ↓
     JSON site export
          ↓
   Static web explorer
```

Person profiles are provisional. Where a source row has no birth year, the
local identity model may infer a birth-year cohort from the recorded age;
rows with neither signal remain in an unresolved name group. These inferred
groups are flagged for review and are not confirmed real-world identities.

To run the repository checks:

```bash
python scripts/check_repo_hygiene.py
node tests/metrics.test.js
```

## Source and attribution

This project is an independent exploration of the [Himalayan
Database](https://www.himalayandatabase.com/), the expedition archives of
Elizabeth Hawley. The local pipeline uses a downloaded snapshot and should be
rebuilt only by a user who has obtained and accepted the database's current
terms. The [official database guide and terms](https://www.himalayandatabase.com/downloads/Himalayan%20Database%20Guide.pdf)
state: “When use is permitted, all extracts, reports and analyses from the
Himalayan Database must be credited to ‘The Himalayan Database ©.’” The same
terms say that extracts, reports, and analyses may not be used or republished
without consent, and that database content may not be copied or linked to
internet websites without prior written permission.

The database was developed from Elizabeth Hawley's expedition records with
Richard Salisbury's database and computing work. This project is an independent
interface and analysis layer; it is not the official Himalayan Database and
does not alter the source archive.

No official database files or generated extracts are included in this public
repository. The site is therefore a local, derived-data explorer until
publication permission is obtained.
