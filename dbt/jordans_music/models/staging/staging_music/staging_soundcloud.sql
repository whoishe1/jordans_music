with
all_soundcloud as (
    select
        trackname,
        artists,
        date_created,
        name_of_playlist,
        row_number() over (partition by trackname,artists order by date_created desc) as track_order
    from {{ source('jordans-music','soundcloud')}}
)
select 
    trackname,
    artists,
    date_created,
    name_of_playlist,
    '{{invocation_id}}' as invocation_id
from all_soundcloud
where track_order = 1
