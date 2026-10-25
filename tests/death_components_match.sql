select id
from {{ ref('mart_expeditions') }}
where coalesce(member_deaths, 0) + coalesce(hired_deaths, 0) <> coalesce(deaths, 0)
