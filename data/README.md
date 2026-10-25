# Data

The app's `dist/*.json` files are generated website exports. The compact bronze
inputs at `data/bronze/` are generated from a local official Himalayan Database
download. None of the raw database, bronze extracts, DuckDB file, or website
exports are checked in or redistributed by this repository.

These exports are local-only and must not be uploaded to a public static host.

Source: [Himalayan Database downloads](https://www.himalayandatabase.com/downloads.html)

The bronze layer includes `expeditions.json`, `peaks.json`, and compressed `members.json.gz`. The
member export is one row per source member-on-expedition record; the dbt layer
turns it into `fct_expedition_member` and a heuristic `dim_person`.

To rebuild the index locally:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_data.py "/path/to/Himalayan Database.zip"
```

The app preserves separate team size, hired-staff count, summiter count,
death count, claimed flag, and disputed flag so its definitions can be changed
without pretending the source data has one unquestionable success rate.
