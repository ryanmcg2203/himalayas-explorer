{{ config(materialized='table') }}

select
    person_key,
    min(full_name) as display_name,
    min(identity_year_of_birth) as year_of_birth,
    min(citizenship) as citizenship,
    count(*) as expedition_appearances,
    count(distinct year) as active_years,
    min(year) as first_year,
    max(year) as last_year,
    case
        when bool_or(identity_method = 'unresolved_name_citizenship')
            or bool_or(identity_method = 'age_inferred_name_citizenship')
            or count(*) > 100
            or max(year) - min(year) >= 50 then 'review'
        when min(identity_year_of_birth) is not null
            and nullif(trim(min(citizenship)), '') is not null then 'moderate'
        else 'low'
    end as identity_confidence,
    case
        when bool_or(identity_method = 'unresolved_name_citizenship')
            then 'unresolved_name_citizenship'
        when bool_or(identity_method = 'age_inferred_name_citizenship')
            then 'age_inferred_name_citizenship'
        else 'Name, birth year, and citizenship match'
    end as identity_method
from {{ ref('fct_expedition_member') }}
where full_name <> ''
group by 1
