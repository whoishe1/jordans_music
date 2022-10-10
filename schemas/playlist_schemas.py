from google.cloud import bigquery

spotify_schema = [
    bigquery.SchemaField("track_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("artists", "STRING"),
    bigquery.SchemaField("trackname", "STRING"),
    bigquery.SchemaField("album", "STRING"),
    bigquery.SchemaField("date_created", "TIMESTAMP"),
    bigquery.SchemaField("name_of_playlist", "STRING"),
]


soundcloud_schema = [
    bigquery.SchemaField("trackname", "STRING"),
    bigquery.SchemaField("artists", "STRING"),
    bigquery.SchemaField("date_created", "TIMESTAMP"),
    bigquery.SchemaField("name_of_playlist", "STRING"),
]
