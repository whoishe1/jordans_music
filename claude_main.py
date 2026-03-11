import datetime
import os
from pathlib import Path

import pandas as pd
from dotenv import dotenv_values

from claude.baselogger import logger
from claude.gcs import LoadData
from claude.playlist_schemas import spotify_schema
from claude.soundcloud_songs import GetSoundCloud
from claude.spotify_songs import GetSpotifyPlaylist

config = dotenv_values(".env")

CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

SPOTIFY_PLAYLISTS = [
    "FUNKSOULJAZZBREAKPIANO",
    "ROCK",
    "the three",
    "the two",
    "the one",
]

SOUNDCLOUD_URL = "https://soundcloud.com/whoishe1/sets"

DATA_DIR = Path("data")


def save_spotify():
    spotify = GetSpotifyPlaylist(
        username=config["USERNAME"],
        scope="playlist-read-private",
        client_id=config["CLIENT_ID"],
        client_secret=config["CLIENT_SECRET"],
        redirect_uri=config["REDIRECT_URI"],
    )

    dfs = [spotify.get_playlists(name) for name in SPOTIFY_PLAYLISTS]
    all_df = pd.concat(dfs).reset_index(drop=True)

    all_df.to_csv(
        DATA_DIR / "spotify" / f"spotify_{CURRENT_DATE}.csv",
        index=False,
        encoding="UTF-8",
    )


def save_soundcloud():
    sc = GetSoundCloud(SOUNDCLOUD_URL)

    urls = sc.which_playlists()
    dfs = [sc.get_playlist(url) for url in urls]

    # reverse so earliest playlist comes first
    all_df = pd.concat(reversed(dfs)).reset_index(drop=True)

    all_df.to_csv(
        DATA_DIR / "soundcloud" / f"soundcloud_{CURRENT_DATE}.csv",
        index=False,
        encoding="UTF-8",
    )


def upload_to_google():
    loader = LoadData(
        service_account=os.path.join(
            os.path.dirname(__file__), "util", "cred", "jordans-cred.json"
        ),
        googlescopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/bigquery",
        ],
        project="jordans-music-343121",
        bucket_name="jordans_music",
    )

    loader.to_gcs_spec()
    loader.gcs_staging("spotify")

    loader.to_bq(
        schema=spotify_schema,
        dataset_name="music",
        table_name="spotify",
        subfolder="spotify_staging",
        name_of_csv="spotify",
    )


def main():
    try:
        print("Saving Spotify playlists...")
        save_spotify()

        print("Uploading to Google Cloud...")
        upload_to_google()

    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"There was an error in scraping/uploading playlists: {e}")
    else:
        print("Successfully pulled playlists and uploaded to GCS and BigQuery")
        logger.info("Successfully pulled playlists and uploaded to GCS and BigQuery")


if __name__ == "__main__":
    main()
