{{ config(materialized='table') }}

-- This is a deliberately cautious identity key, not a claim of perfect
-- identity resolution. Name, year of birth, and citizenship are the available
-- signals in the compact member export; aliases remain visible in the fact.
select
    md5(lower(regexp_replace(trim(full_name), '\\s+', ' ', 'g')) || '|' || coalesce(year_of_birth, '') || '|' || lower(trim(coalesce(citizenship, '')))) as person_key,
    min(full_name) as display_name,
    min(year_of_birth) as year_of_birth,
    min(citizenship) as citizenship,
    count(*) as expedition_appearances,
    'heuristic_name_yob_citizenship' as identity_method
from {{ ref('stg_members') }}
where full_name <> ''
group by 1
