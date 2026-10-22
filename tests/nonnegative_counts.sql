select id
from {{ ref('mart_expeditions') }}
where team < 0
   or hired < 0
   or summiters < 0
   or summit_hired < 0
   or deaths < 0
