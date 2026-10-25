select person_key
from {{ ref('mart_person_profile') }}
where appearances < 1
   or first_year > last_year
   or identity_reason is null
   or possible_merge is null
