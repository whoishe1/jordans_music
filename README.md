# Personal playlists extractions

- Transfer my playlists from spotify and soundcloud to Google Cloud Storage and BigQuery
- Needed Transformation in DBT
- Visualizations in Power BI

# Instructions

- dbt will be ran on a separate `virtualenv` and the app that pulls data and loads the data into BigQuery will be in another `virtualenv`, this is because dbt relies on a different version of Google API libraries
