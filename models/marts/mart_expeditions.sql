{{ config(materialized='table') }}

select
    id,
    source_id,
    case
        when year < 1950 then 'early'
        when year < 1970 then 'expeditionary'
        when year < 1990 then 'transitional'
        else 'commercial'
    end as era,
    year,
    mountain,
    peak_id,
    team_members as team,
    hired_staff as hired,
    team_members + hired_staff as participants,
    recorded_summiters as summiters,
    hired_summiters as summit_hired,
    member_summiters,
    deaths,
    member_deaths,
    hired_deaths,
    source_outcome as result,
    case
        when source_outcome = 'summit' then 'Summit'
        when source_outcome = 'fail' then 'Tragedy'
        else 'Turned back'
    end as label,
    style,
    oxygen,
    leader_or_role,
    leader_kind,
    leader_name,
    nation,
    route,
    route2,
    route3,
    route4,
    lower(trim(route)) as route_normalized,
    lower(trim(route2)) as route2_normalized,
    lower(trim(route3)) as route3_normalized,
    lower(trim(route4)) as route4_normalized,
    host,
    season,
    disputed,
    claimed,
    has_recorded_summit,
    has_member_summit,
    has_undisputed_summit
from {{ ref('int_expeditions_classified') }}
