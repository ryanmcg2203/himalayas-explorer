# Data

The app's `dist/expeditions.json` is the website export. The compact bronze
input at `data/bronze/expeditions.json` is generated from the official
Himalayan Database download. The raw database is not checked in.

Source: [Himalayan Database downloads](https://www.himalayandatabase.com/downloads.html)

The bronze layer includes `expeditions.json` and compressed `members.json.gz`. The
member export is one row per source member-on-expedition record; the dbt layer
turns it into `fct_expedition_member` and a heuristic `dim_person`.

The current source used for the prototype is version 2.75 with the Autumn–Winter
2025 update. To rebuild the index:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_data.py "/path/to/Himalayan Database.zip"
```

The app preserves separate team size, hired-staff count, summiter count,
death count, claimed flag, and disputed flag so its definitions can be changed
without pretending the source data has one unquestionable success rate.
