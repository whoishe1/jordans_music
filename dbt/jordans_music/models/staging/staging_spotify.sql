{{ config(schema='staging') }}

select 
    (track_id || '-' || artists || '-' || trackname) as unique_code
    ,track_id
    ,artists	
    ,trackname
    ,album
from {{ source('jordans-music-343121','spotify')}}