with 
all_soundcloud as (
    select 
        trackname,
        artists,
        row_number () over (partition by trackname,artists order by trackname) as track_order,
        name_of_playlist,
        '{{invocation_id}}' as invocation_id
    from {{ source('jordans-music','soundcloud') }}
    where artists is not null and trackname is not null
)
select
    trackname,
    artists,
    track_order,
    name_of_playlist,
    invocation_id
from all_soundcloud
