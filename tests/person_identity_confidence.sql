select person_key
from {{ ref('dim_person') }}
where identity_confidence not in ('low', 'moderate', 'review')
   or (identity_confidence = 'review' and expedition_appearances <= 100 and last_year - first_year < 50)
