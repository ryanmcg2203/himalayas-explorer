{{ config(materialized='view') }}

select
    id,
    sourceId as source_id,
    cast(year as integer) as year,
    mountain,
    peakId as peak_id,
    cast(team as integer) as team_members,
    cast(hired as integer) as hired_staff,
    cast(summiters as integer) as summiters,
    cast(summitHired as integer) as hired_summiters,
    cast(deaths as integer) as deaths,
    result as source_result,
    label as source_label,
    style,
    oxygen,
    leader,
    nation,
    route,
    cast(season as integer) as season,
    cast(disputed as boolean) as disputed,
    cast(claimed as boolean) as claimed
from read_json_auto('data/bronze/expeditions.json')
