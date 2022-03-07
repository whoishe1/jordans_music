{{ config(schema='staging') }}

select 
    trackname	
    ,artists
from {{ source('jordans-music-343121','soundcloud') }}