select id, era
from {{ ref('mart_expeditions') }}
where era not in ('early', 'expeditionary', 'transitional', 'commercial')
   or (year < 1950 and era <> 'early')
   or (year between 1950 and 1969 and era <> 'expeditionary')
   or (year between 1970 and 1989 and era <> 'transitional')
   or (year >= 1990 and era <> 'commercial')
