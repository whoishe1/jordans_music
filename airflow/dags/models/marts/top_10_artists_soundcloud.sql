{{ config(schema='marts') }}

select
    artists
    ,count(artists) as count_artists
    ,'{{invocation_id}}' as invocation_id
from {{ref('staging_soundcloud')}}
group by artists
order by count(artists) desc
limit 10