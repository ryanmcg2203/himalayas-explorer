{{ config(materialized='view') }}

select
    *,
    nullif(trim(leader), '') as leader_or_role,
    case
        when nullif(trim(leader), '') is null then 'not_recorded'
        when lower(trim(leader)) in ('sherpa rope-fixing', 'tibetan rope-fixing') then 'role'
        else 'named_leader'
    end as leader_kind,
    case
        when nullif(trim(leader), '') is null then null
        when lower(trim(leader)) in ('sherpa rope-fixing', 'tibetan rope-fixing') then null
        else nullif(trim(leader), '')
    end as leader_name,
    summiters as member_summiters,
    summiters + hired_summiters as recorded_summiters,
    (summiters + hired_summiters) > 0 as has_recorded_summit,
    summiters > 0 as has_member_summit,
    (summiters + hired_summiters > 0 and not disputed) as has_undisputed_summit,
    case
        when summiters + hired_summiters > 0 then 'summit'
        when deaths > 0 then 'fail'
        else 'mixed'
    end as source_outcome
from {{ ref('stg_expeditions') }}
