select expedition_member_id
from {{ ref('fct_expedition_member') }}
where not matched_expedition
