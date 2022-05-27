select 
    (track_id || '-' || artists || '-' || trackname) as unique_code
    ,track_id
    ,artists	
    ,trackname
    ,album
    ,'{{invocation_id}}' as invocation_id
from {{ source('jordans-music','spotify')}}