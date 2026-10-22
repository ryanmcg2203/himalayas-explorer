select id
from {{ ref('mart_expeditions') }}
where summiters > team
