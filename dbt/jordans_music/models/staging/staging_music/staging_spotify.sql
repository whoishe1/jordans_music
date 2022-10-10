with
all_spotify as (
    select
        track_id,
        artists,
        trackname,
        album,
        name_of_playlist,
        date_created,
        row_number () over (partition by track_id,artists order by date_created desc) as track_order
    from {{ source('jordans-music','spotify') }}
)
select
      track_id,
      artists,
      trackname,
      album,
      name_of_playlist,
      date_created,
      '{{invocation_id}}' as invocation_id
from all_spotify
where track_order = 1