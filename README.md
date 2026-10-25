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

## Run it

The repository contains code and documentation only. To build the local
snapshot and run the explorer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_data.py "/path/to/Himalayan Database.zip"
DBT_PROFILES_DIR=. dbt build
python scripts/export_site_data.py
python3 -m http.server 4173 --directory dist
```

Then open <http://127.0.0.1:4173>. If port 4173 is already in use, stop the
existing local server or choose another port.

The peak stats sheet is available at
<http://127.0.0.1:4173/peak.html?peak=Everest> after the local data rebuild.

The peak browser is available at <http://127.0.0.1:4173/peaks.html>.

The provisional climber browser and profile pages are available at
<http://127.0.0.1:4173/people.html>.

The expedition index and individual records are available at
<http://127.0.0.1:4173/expeditions.html> and
<http://127.0.0.1:4173/expedition.html?id=1953-...>.

The dbt models live in `models/` and the semantic checks live in `tests/`. The
DuckDB file and generated JSON exports are intentionally local. The member
layer and provisional identity model are rebuilt from the same snapshot; do
not treat a profile as a confirmed real-world identity.

To rebuild from a newer official snapshot, download the current database
archive from the [Himalayan Database downloads page](https://www.himalayandatabase.com/downloads.html)
and repeat the commands above.

The raw archive, bronze extracts (including peak metadata), DuckDB database, and static JSON exports are
not checked in. They are ignored locally. The importer creates stable IDs for
source IDs that collide across centuries, while preserving the original source
ID.

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
