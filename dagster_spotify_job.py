import datetime
import os

import pandas as pd
from dotenv import load_dotenv
from dagster import job, op

from schemas.playlist_schemas import soundcloud_schema, spotify_schema
from util.gcs import LoadData
from util.soundcloud_songs import GetSoundCloud
from util.spotify_songs import GetSpotifyPlaylist

load_dotenv()

CRED_PATH = os.path.join(os.path.dirname(__file__), "util/cred/jordans-cred.json")
GOOGLE_SCOPES_GCS = ["https://www.googleapis.com/auth/cloud-platform"]
GOOGLE_SCOPES_BQ = ["https://www.googleapis.com/auth/bigquery"]
PROJECT = "jordans-music-343121"
BUCKET_NAME = "jordans_music"
SOUNDCLOUD_URL = "https://soundcloud.com/jordan-lee-375/sets"
DATASET_NAME = "music"
DATE_STR = datetime.date.today().strftime("%Y-%m-%d")


@op
def save_soundcloud(context) -> str:
    sc = GetSoundCloud(url=SOUNDCLOUD_URL)
    playlist_urls = sc.which_playlists()
    for url in playlist_urls:
        df = sc.getplaylist(url)
        playlist_name = url.split("/")[-1]
        output_path = os.path.join("data", "soundcloud", f"soundcloud_{playlist_name}_{DATE_STR}.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        context.log.info(f"Saved SoundCloud playlist '{playlist_name}' to {output_path}")
    return "soundcloud_done"


@op
def save_spotify(context) -> str:
    sp = GetSpotifyPlaylist(
        username=os.environ["USERNAME"],
        scope="playlist-read-private",
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        redirect_uri=os.environ["REDIRECT_URI"],
    )
    playlists = sp.my_playlists()
    all_dfs = []
    for playlist_name in playlists:
        df = sp.get_playlists(playlist_name)
        if df is not None:
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs).reset_index(drop=True)
        output_path = os.path.join("data", "spotify", f"spotify_{DATE_STR}.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        combined.to_csv(output_path, index=False)
        context.log.info(f"Saved {len(combined)} Spotify tracks to {output_path}")
    return "spotify_done"


@op
def gcs_bq_google(context, soundcloud_status: str, spotify_status: str):
    context.log.info(f"Upstream statuses: {soundcloud_status}, {spotify_status}")

    loader = LoadData(
        service_account=CRED_PATH,
        googlescopes=GOOGLE_SCOPES_GCS,
        project=PROJECT,
        bucket_name=BUCKET_NAME,
    )

    loader.to_gcs_spec()
    context.log.info("Uploaded date-stamped CSVs to GCS")

    for source in ("spotify", "soundcloud"):
        loader.gcs_staging(source)
        context.log.info(f"Uploaded {source} staging CSV to GCS")

    loader_bq = LoadData(
        service_account=CRED_PATH,
        googlescopes=GOOGLE_SCOPES_BQ,
        project=PROJECT,
        bucket_name=BUCKET_NAME,
    )
    loader_bq.to_bq(
        schema=spotify_schema,
        dataset_name=DATASET_NAME,
        table_name="spotify",
        subfolder="spotify_staging",
        name_of_csv="spotify",
    )
    context.log.info("Loaded Spotify staging data into BigQuery")

    loader_bq.to_bq(
        schema=soundcloud_schema,
        dataset_name=DATASET_NAME,
        table_name="soundcloud",
        subfolder="soundcloud_staging",
        name_of_csv="soundcloud",
    )
    context.log.info("Loaded SoundCloud staging data into BigQuery")


@job
def playlist_job():
    sc = save_soundcloud()
    sp = save_spotify()
    gcs_bq_google(sc, sp)
