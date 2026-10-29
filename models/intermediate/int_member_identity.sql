{{ config(materialized='view') }}

-- The source does not provide a dependable global person ID. Keep the raw
-- name/year-of-birth/citizenship key, but use age-derived cohorts when the
-- source row has no birth year. Rows with neither signal remain unresolved.
with base as (
    select
        m.*,
        md5(lower(regexp_replace(trim(m.full_name), '\\s+', ' ', 'g')) || '|' ||
            coalesce(m.year_of_birth, '') || '|' ||
            lower(trim(coalesce(m.citizenship, '')))) as source_person_key,
        case
            when m.year_of_birth is not null then cast(m.year_of_birth as integer)
            when m.age between 16 and 80 then m.year - m.age
            else null
        end as identity_year_of_birth
    from {{ ref('stg_members') }} m
), resolved as (
    select
        *,
        md5(lower(regexp_replace(trim(full_name), '\\s+', ' ', 'g')) || '|' ||
            coalesce(cast(identity_year_of_birth as varchar), '') || '|' ||
            lower(trim(coalesce(citizenship, '')))) as person_key,
        case
            when year_of_birth is not null then 'source_name_yob_citizenship'
            when identity_year_of_birth is not null then 'age_inferred_name_citizenship'
            else 'unresolved_name_citizenship'
        end as identity_method
    from base
)
select *
from resolved
