{{ config(severity='warn') }}

with roster as (
    select
        expedition_id,
        sum(case when not is_hired and summit_success then 1 else 0 end) as roster_member_summits,
        sum(case when is_hired and summit_success then 1 else 0 end) as roster_hired_summits,
        sum(case when not is_hired and died then 1 else 0 end) as roster_member_deaths,
        sum(case when is_hired and died then 1 else 0 end) as roster_hired_deaths
    from {{ ref('fct_expedition_member') }}
    where full_name <> ''
    group by expedition_id
)

select e.id
from {{ ref('mart_expeditions') }} e
left join roster r on r.expedition_id = e.id
where coalesce(r.roster_member_summits, 0) <> e.member_summiters
   or coalesce(r.roster_hired_summits, 0) <> e.summit_hired
   or coalesce(r.roster_member_deaths, 0) <> e.member_deaths
   or coalesce(r.roster_hired_deaths, 0) <> e.hired_deaths
