import datetime
import os
from pathlib import Path

import pandas as pd
from dagster import job, op
from dotenv import dotenv_values

from claude.gcs import LoadData
from claude.playlist_schemas import spotify_schema
from claude.soundcloud_songs import GetSoundCloud
from claude.spotify_songs import GetSpotifyPlaylist

config = dotenv_values(".env")

SPOTIFY_PLAYLISTS = [
    "FUNKSOULJAZZBREAKPIANO",
    "ROCK",
    "the three",
    "the two",
    "the one",
]

SOUNDCLOUD_URL = "https://soundcloud.com/whoishe1/sets"
DATA_DIR = Path("data")
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

CRED_PATH = os.path.join(os.path.dirname(__file__), "util", "cred", "jordans-cred.json")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/bigquery",
]
PROJECT = "jordans-music-343121"
BUCKET_NAME = "jordans_music"
DATASET_NAME = "music"


@op
def save_soundcloud(context) -> str:
    sc = GetSoundCloud(SOUNDCLOUD_URL)
    urls = sc.which_playlists()
    dfs = [sc.get_playlist(url) for url in urls]
    all_df = pd.concat(reversed(dfs)).reset_index(drop=True)
    output_path = DATA_DIR / "soundcloud" / f"soundcloud_{CURRENT_DATE}.csv"
    all_df.to_csv(output_path, index=False, encoding="UTF-8")
    context.log.info(f"Saved {len(all_df)} SoundCloud tracks to {output_path}")
    return "soundcloud_done"


@op
def save_spotify(context) -> str:
    spotify = GetSpotifyPlaylist(
        username=config["USERNAME"],
        scope="playlist-read-private",
        client_id=config["CLIENT_ID"],
        client_secret=config["CLIENT_SECRET"],
        redirect_uri=config["REDIRECT_URI"],
    )
    dfs = [spotify.get_playlists(name) for name in SPOTIFY_PLAYLISTS]
    all_df = pd.concat(dfs).reset_index(drop=True)
    output_path = DATA_DIR / "spotify" / f"spotify_{CURRENT_DATE}.csv"
    all_df.to_csv(output_path, index=False, encoding="UTF-8")
    context.log.info(f"Saved {len(all_df)} Spotify tracks to {output_path}")
    return "spotify_done"


@op
def gcs_bq_google(context, soundcloud_status: str, spotify_status: str):
    context.log.info(f"Upstream statuses: {soundcloud_status}, {spotify_status}")

    loader = LoadData(
        service_account=CRED_PATH,
        googlescopes=GOOGLE_SCOPES,
        project=PROJECT,
        bucket_name=BUCKET_NAME,
    )

    loader.to_gcs_spec()
    context.log.info("Uploaded date-stamped CSVs to GCS")

    loader.gcs_staging("spotify")
    context.log.info("Uploaded Spotify staging CSV to GCS")

    loader.to_bq(
        schema=spotify_schema,
        dataset_name=DATASET_NAME,
        table_name="spotify",
        subfolder="spotify_staging",
        name_of_csv="spotify",
    )
    context.log.info("Loaded Spotify data into BigQuery")


@job
def playlist_job():
    sc = save_soundcloud()
    sp = save_spotify()
    gcs_bq_google(sc, sp)
