from dagster import (
    job,
    op,
    Nothing,
    In,
    success_hook,
    failure_hook,
    HookContext,
)
import pandas as pd
from dotenv import dotenv_values
from util.soundcloud_songs import GetSoundCloud
from util.spotify_songs import GetSpotifyPlaylist
from util.gcs import LoadData
from schemas.playlist_schemas import spotify_schema, soundcloud_schema
import os
import datetime

config = dotenv_values(".env")

current_date = datetime.datetime.now().strftime("%Y-%m-%d")


@failure_hook
def general_failure(context: HookContext):
    message = f"Op {context.op.name} failed"
    print(message)
    # op_exception: BaseException = context.op_exception
    # # print stack trace of exception
    # traceback.print_tb(op_exception.__traceback__)


@success_hook
def general_success(context: HookContext):
    message = f"Op {context.op.name} finished successfully"
    print(message)


@op(ins={"Second": In(Nothing)})
def save_spotify():
    """Executes Spotify script that gets all playlists"""

    alltracks_obj = GetSpotifyPlaylist(
        username=config["USERNAME"],
        scope="playlist-read-private",
        client_id=config["CLIENT_ID"],
        client_secret=config["CLIENT_SECRET"],
    )

    pl = [
        "FUNKSOULJAZZ",
        "lp",
        "the six",
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


@op(ins={"First": In(Nothing)})
def save_soundcloud():
    """Executes soundcloud script that gets all playlists"""

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


@op(ins={"Third": In(Nothing)})
def gcs_bq_google():
    """Connects to Google Cloud Storage and BigQuery and uploads staging data"""

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


@job(hooks={general_failure, general_success})
def playlist_job():
    gcs_bq_google(save_spotify(save_soundcloud()))
