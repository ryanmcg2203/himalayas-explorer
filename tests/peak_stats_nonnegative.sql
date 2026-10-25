select peak_id
from {{ ref('mart_peaks') }}
where expeditions < 0
   or member_attempts < 0
   or member_summits < 0
   or member_deaths < 0
   or hired_deaths < 0
   or deaths < 0
   or (member_attempts = 0 and member_summit_rate is not null)
