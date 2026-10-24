select id, leader_kind
from {{ ref('mart_expeditions') }}
where leader_kind not in ('named_leader', 'role', 'not_recorded')
   or (lower(trim(leader_or_role)) in ('sherpa rope-fixing', 'tibetan rope-fixing') and leader_kind <> 'role')
   or (leader_kind = 'role' and leader_name is not null)

