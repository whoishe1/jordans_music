import pandas as pd
from dotenv import dotenv_values
from util.soundcloud_songs import GetSoundCloud
from util.spotify_songs import GetSpotifyPlaylist
from util.baselogger import logger
from util.gcs import LoadData
from schemas.playlist_schemas import spotify_schema, soundcloud_schema
import time
import os
import datetime

config = dotenv_values(".env")

current_date = datetime.datetime.now().strftime("%Y-%m-%d")


def save_spotify():
    alltracks_obj = GetSpotifyPlaylist(
        username=config["USERNAME"],
        scope="playlist-read-private",
        client_id=config["CLIENT_ID"],
        client_secret=config["CLIENT_SECRET"],
    )

    pl = [
        "FUNK AND SOUL",
        "lp",
        "the six",
        "the five",
        "the three",
        "the two",
        "the one",
    ]

    output = []
    for i in pl:
        df = alltracks_obj.get_playlists(i)
        output.append(df)

    all_df = pd.concat(output).reset_index(drop=True)

    all_df.to_csv(
        os.path.join(r"./data/spotify", f"spotify_{current_date}.csv"),
        index=False,
        encoding="UTF-8",
    )


def save_soundcloud():
    URL = "https://soundcloud.com/whoishe1/sets"
    playlist_dfs = []
    sc = GetSoundCloud(URL)

    urls = sc.which_playlists()
    for i in urls:
        this_df = sc.getplaylist(i)
        playlist_dfs.append(this_df)

    # sort order by first playlist
    playlist_order = playlist_dfs[::-1]

    total_playlist = pd.concat(playlist_order).reset_index(drop=True)

    total_playlist.to_csv(
        os.path.join(r"./data/soundcloud", f"soundcloud_{current_date}.csv"),
        index=False,
        encoding="UTF-8",
    )


def main():
    try:
        print("Saving Soundcloud and Spotify playlists")
        # save_soundcloud()
        save_spotify()
        time.sleep(1)

        to_google = LoadData(
            service_account=os.path.join(
                os.path.dirname(__file__), "util\\cred\\jordans-cred.json"
            ),
            googlescopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/bigquery",
            ],
            project="jordans-music-343121",
            bucket_name="jordans_music",
        )

        # upload pulled playlist on current date
        to_google.to_gsc_spec()

        # # Merge playlists together and get 1 raw data table for each source to upload to bigquery
        to_google.gsc_staging("spotify")
        to_google.gsc_staging("soundcloud")

        # # upload raw data to bigquery
        to_google.to_bq(
            schema=spotify_schema,
            dataset_name="music",
            table_name="spotify",
            subfolder="spotify_staging",
            name_of_csv="spotify",
        )
        to_google.to_bq(
            schema=soundcloud_schema,
            dataset_name="music",
            table_name="soundcloud",
            subfolder="soundcloud_staging",
            name_of_csv="soundcloud",
        )

    except Exception as e:
        print(f"error due to {e}")
        logger.error("There was an error in scraping/uploading playlists: {e}")

    else:
        print(
            "succesfully pulled playlists and uploaded in google storage and BigQuery"
        )
        logger.info(
            "succesfully pulled playlists and uploaded in google storage and BigQuery"
        )


if __name__ == "__main__":
    main()
