{{ config(materialized='table') }}

with activity as (
    select
        person_key,
        count(*) as appearances,
        sum(cast(summit_success as integer)) as summits,
        sum(cast(died as integer)) as deaths,
        sum(cast(is_hired as integer)) as hired_appearances,
        count(distinct mountain) as peak_count,
        min(year) as first_year,
        max(year) as last_year,
        to_json(list(distinct mountain order by mountain)) as peaks,
        to_json(list(distinct year order by year)) as years
    from {{ ref('fct_expedition_member') }}
    where full_name <> ''
    group by person_key
), peak_counts as (
    select person_key, peak_id, mountain,
           row_number() over (partition by person_key order by count(*) desc, mountain) as rank
    from {{ ref('fct_expedition_member') }}
    where full_name <> ''
        group by person_key, peak_id, mountain
)

select
    d.person_key,
    d.display_name,
    d.year_of_birth,
    d.citizenship,
    d.identity_confidence,
    d.identity_method,
    case
        when d.identity_method = 'unresolved_name_citizenship'
            then 'No birth year or age signal; unresolved name group'
        when d.identity_method = 'age_inferred_name_citizenship'
            then 'Birth year inferred from age; review match'
        when d.year_of_birth is null and nullif(trim(coalesce(d.citizenship, '')), '') is null
            then 'No birth year or citizenship recorded'
        when d.year_of_birth is null then 'No birth year recorded'
        when nullif(trim(coalesce(d.citizenship, '')), '') is null then 'No citizenship recorded'
        when a.last_year - a.first_year >= 50 then 'Long active span; possible merge'
        when a.appearances > 100 then 'High record count; possible merge'
        else 'Name, birth year, and citizenship match'
    end as identity_reason,
    a.appearances,
    a.summits,
    a.deaths,
    a.hired_appearances,
    a.peak_count,
    a.first_year,
    a.last_year,
    a.peaks,
    a.years,
    p.peak_id as top_peak_id,
    p.mountain as top_peak,
    (a.last_year - a.first_year >= 60 or a.appearances > 100) as possible_merge
from {{ ref('dim_person') }} d
join activity a using (person_key)
left join peak_counts p on p.person_key = a.person_key and p.rank = 1
