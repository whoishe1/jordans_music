select 
    trackname	
    ,artists
    ,'{{invocation_id}}' as invocation_id
from {{ source('jordans-music','soundcloud') }}