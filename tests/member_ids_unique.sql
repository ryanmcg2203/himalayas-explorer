select expedition_member_id
from {{ ref('fct_expedition_member') }}
group by expedition_member_id
having count(*) > 1
