{{ config(schema='marts') }}

select
    artists
    ,count(artists) as count_artists
from {{ref('staging_spotify')}}
group by artists
order by count(artists) desc
limit 10