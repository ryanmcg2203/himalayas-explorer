{{ config(materialized='view') }}

select
    *,
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
