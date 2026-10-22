{{ config(materialized='table') }}

select
    mountain,
    year,
    count(*) as expeditions,
    sum(case when has_recorded_summit then 1 else 0 end) as recorded_successes,
    sum(case when has_member_summit then 1 else 0 end) as member_successes,
    sum(case when has_undisputed_summit then 1 else 0 end) as undisputed_successes,
    sum(team_members) as team_members,
    sum(summiters) as summiters,
    sum(deaths) as deaths
from {{ ref('int_expeditions_classified') }}
group by 1, 2
