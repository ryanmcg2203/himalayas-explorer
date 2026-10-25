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

This is a local-only build. First obtain the current archive from the
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

The dbt models live in `models/` and the semantic checks live in `tests/`. The
raw archive, bronze extracts, DuckDB database, and static JSON exports are
ignored locally. The importer creates stable IDs for source IDs that collide
across centuries while preserving the original source ID.

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

No official database files or generated extracts are included in this public
repository. The site is therefore a local, derived-data explorer until
publication permission is obtained.
