select person_key
from {{ ref('dim_person') }}
where identity_confidence not in ('low', 'moderate', 'review')
   or (identity_confidence = 'review'
       and identity_method not in ('age_inferred_name_citizenship', 'unresolved_name_citizenship')
       and expedition_appearances <= 100
       and last_year - first_year < 50)
