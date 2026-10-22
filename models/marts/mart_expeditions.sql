{{ config(materialized='table') }}

select
    id,
    source_id,
    year,
    mountain,
    peak_id,
    team_members as team,
    hired_staff as hired,
    summiters,
    hired_summiters as summit_hired,
    member_summiters,
    deaths,
    source_outcome as result,
    case
        when source_outcome = 'summit' then 'Summit'
        when source_outcome = 'fail' then 'Tragedy'
        else 'Turned back'
    end as label,
    style,
    oxygen,
    leader,
    nation,
    route,
    season,
    disputed,
    claimed,
    has_recorded_summit,
    has_member_summit,
    has_undisputed_summit
from {{ ref('int_expeditions_classified') }}
