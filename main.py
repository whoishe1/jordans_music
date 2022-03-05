import pandas as pd
from dotenv import dotenv_values
from util.soundcloud_songs import GetSoundCloud
from util.spotify_songs import GetSpotifyPlaylist
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

    pl = ["lp", "the six", "the five", "the three", "the two", "the one"]

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
