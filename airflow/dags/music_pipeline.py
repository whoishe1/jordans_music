from __future__ import annotations

import datetime
import os

import pandas as pd
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from dotenv import dotenv_values

config = dotenv_values(".env")

SPOTIFY_PLAYLISTS = ["FUNKSOULJAZZ", "lp", "the six", "the three", "the two", "the one"]
SOUNDCLOUD_URL = "https://soundcloud.com/whoishe1/sets"
GCS_PROJECT = "jordans-music-343121"
GCS_BUCKET = "jordans_music"
CRED_PATH = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
DBT_PROJECT_DIR = "/home/airflow/gcs/data/project"
DBT_PROFILES_DIR = "/home/airflow/gcs/data/profiles"


@dag(
    dag_id="music_pipeline",
    description="Extract Spotify & SoundCloud playlists, load to GCS/BigQuery, run dbt",
    schedule="@daily",
    start_date=datetime.datetime(2024, 1, 1),
    catchup=False,
    default_args={
        "owner": "Jordan",
        "retries": 1,
        "retry_delay": datetime.timedelta(minutes=5),
    },
    tags=["music", "spotify", "soundcloud"],
)
def music_pipeline():
    @task()
    def extract_soundcloud() -> str:
        from util.soundcloud_songs import GetSoundCloud

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join(
            "./data/soundcloud", f"soundcloud_{current_date}.csv"
        )

        sc = GetSoundCloud(SOUNDCLOUD_URL)
        urls = sc.which_playlists()

        playlist_dfs = [sc.getplaylist(url) for url in urls]
        playlist_order = playlist_dfs[::-1]

        total_playlist = pd.concat(playlist_order).reset_index(drop=True)
        total_playlist.to_csv(output_path, index=False, encoding="UTF-8")

        return output_path

    @task()
    def extract_spotify(soundcloud_path: str) -> str:
        from util.spotify_songs import GetSpotifyPlaylist

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join("./data/spotify", f"spotify_{current_date}.csv")

        client = GetSpotifyPlaylist(
            username=config["USERNAME"],
            scope="playlist-read-private",
            client_id=config["CLIENT_ID"],
            client_secret=config["CLIENT_SECRET"],
            redirect_uri=config["REDIRECT_URI"],
        )

        dfs = [client.get_playlists(pl) for pl in SPOTIFY_PLAYLISTS]
        all_df = pd.concat(dfs).reset_index(drop=True)
        all_df.to_csv(output_path, index=False, encoding="UTF-8")

        return output_path

    @task()
    def load_to_gcs_bq(spotify_path: str) -> None:
        from schemas.playlist_schemas import soundcloud_schema, spotify_schema
        from util.gcs import LoadData

        loader = LoadData(
            service_account=CRED_PATH,
            googlescopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/bigquery",
            ],
            project=GCS_PROJECT,
            bucket_name=GCS_BUCKET,
        )

        loader.to_gcs_spec()

        loader.gcs_staging("spotify")
        loader.gcs_staging("soundcloud")

        loader.to_bq(
            schema=spotify_schema,
            dataset_name="music",
            table_name="spotify",
            subfolder="spotify_staging",
            name_of_csv="spotify",
        )
        loader.to_bq(
            schema=soundcloud_schema,
            dataset_name="music",
            table_name="soundcloud",
            subfolder="soundcloud_staging",
            name_of_csv="soundcloud",
        )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"dbt build --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    soundcloud_path = extract_soundcloud()
    spotify_path = extract_spotify(soundcloud_path)
    gcs_task = load_to_gcs_bq(spotify_path)
    gcs_task >> dbt_build


dag = music_pipeline()
