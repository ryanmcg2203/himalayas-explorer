{{ config(materialized='table') }}

with peak_source as (
    select
        cast(peakId as varchar) as peak_id,
        * exclude (peakId)
    from read_json_auto('data/bronze/peaks.json')
), peak_stats as (
    select
        peak_id,
        count(*) as expeditions,
        sum(team) as member_attempts,
        sum(member_summiters) as member_summits,
        sum(member_deaths) as member_deaths,
        sum(hired_deaths) as hired_deaths,
        sum(deaths) as deaths,
        case when sum(team) > 0 then sum(member_summiters) * 100.0 / sum(team) end as member_summit_rate
    from {{ ref('mart_expeditions') }}
    group by peak_id
), decade_stats as (
    select
        peak_id,
        json_group_object(cast(decade as varchar), expedition_count) as decade_counts
    from (
        select peak_id, floor(year / 10) * 10 as decade, count(*) as expedition_count
        from {{ ref('mart_expeditions') }}
        group by peak_id, decade
    ) grouped
    group by peak_id
)

select
    p.*,
    coalesce(s.expeditions, 0) as expeditions,
    coalesce(s.member_attempts, 0) as member_attempts,
    coalesce(s.member_summits, 0) as member_summits,
    coalesce(s.member_deaths, 0) as member_deaths,
    coalesce(s.hired_deaths, 0) as hired_deaths,
    coalesce(s.deaths, 0) as deaths,
    s.member_summit_rate,
    coalesce(d.decade_counts, '{}') as decade_counts
from peak_source p
left join peak_stats s using (peak_id)
left join decade_stats d using (peak_id)
