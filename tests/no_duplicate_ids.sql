select id
from {{ ref('mart_expeditions') }}
group by id
having count(*) > 1
