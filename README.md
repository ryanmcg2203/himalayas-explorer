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

From this directory:

```bash
python3 -m http.server 4173 --directory dist
```

Then open <http://127.0.0.1:4173>.

The peak stats sheet is available at
<http://127.0.0.1:4173/peak.html?peak=Everest> after the local data rebuild.

The peak browser is available at <http://127.0.0.1:4173/peaks.html>.

The provisional climber browser and profile pages are available at
<http://127.0.0.1:4173/people.html>.

The expedition index and individual records are available at
<http://127.0.0.1:4173/expeditions.html> and
<http://127.0.0.1:4173/expedition.html?id=1953-...>.

The static site reads generated JSON exports from `dist/`. Build those exports
locally before opening the site. The reproducible source-to-mart pipeline is
described below and preserves the UI's explicit outcome definitions.

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
`fct_expedition_member` and a cautious, provisional `dim_person`. Person
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

The raw archive, bronze extracts (including peak metadata), DuckDB database, and static JSON exports are
not checked in. They are ignored locally. The importer creates stable IDs for
source IDs that collide across centuries, while preserving the original source
ID.

## Source and attribution

This project is an independent exploration of the [Himalayan
Database](https://www.himalayandatabase.com/), the expedition archives of
Elizabeth Hawley. The local pipeline uses a downloaded snapshot and should be
rebuilt only by a user who has obtained and accepted the database's current
terms. The official terms state that extracts, reports, and analyses intended
for publication require permission, and that permitted use must be credited to
“The Himalayan Database ©.” See the [official database guide and terms](https://www.himalayandatabase.com/downloads/Himalayan%20Database%20Guide.pdf).

No official database files or generated extracts are included in this public
repository. The site is therefore a local, derived-data explorer until
publication permission is obtained.

## Ask questions with MCP

The website is the visual layer. The local MCP server exposes the tested
DuckDB marts as focused tools that an MCP-compatible agent can use to answer
natural-language questions with traceable records and explicit definitions.

After building the database, start the server from the project directory:

```bash
source .venv/bin/activate
python mcp_server.py
```

Configure it as a local stdio server in your MCP client. Use absolute paths in
the client configuration, for example:

```json
{
  "mcpServers": {
    "above-base-camp": {
      "command": "/absolute/path/to/himalayas-explorer/.venv/bin/python",
      "args": ["/absolute/path/to/himalayas-explorer/mcp_server.py"]
    }
  }
}
```

Available tools include expedition and climber search, full expedition evidence
with member rosters, peak comparisons, era comparisons, and metric
definitions. Example questions:

- Compare Everest and Annapurna I per non-hired member from 1990 onward.
- Find climber profiles matching Russell, then show one person's expedition history.
- Compare the early, expeditionary, transitional, and commercial eras.
- Explain the denominator behind this death rate.

The server is deliberately not an LLM or a free-form SQL endpoint: it gives an
agent safe, bounded tools over the already-built DuckDB marts. The natural
language layer comes from the MCP client.
