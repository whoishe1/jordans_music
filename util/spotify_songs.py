import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd


class GetSpotifyPlaylist:
    """Returns Tracks, Artists, and Album of a specified playlists in a pandas/xlsx format

    Attributes:
        username: Spotify username
        scope: Spotify authorization scopes, i.e. 'playlist-read-private'
        client_id: Spotify client id
        client_secret: Spotify client secret
        redirect_url: redirect authorization url

    """

    def __init__(self, username, scope, client_id, client_secret, redirect_uri):
        """Initialize ReturnPlayList"""
        self.username = username
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_connection(self):
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
            )
        )
        return sp

    def my_playlists(self):
        sp = self.get_connection()
        ### the method "user_playlists" not working, returns no playlist information ###
        # playlists = sp.user_playlists(self.username)
        playlists = sp.current_user_playlists(limit=50)
        stored_playlists = [value for idx, value in enumerate(playlists["items"])]
        list_playlists = [i["name"] for i in stored_playlists]
        return list_playlists

    def dataframe_tracks(self, tracks):
        """Helper function that retrieves the tracklist in a json format
        for the specified playlist and outputs it into a pandas dataframe.
        Only outputs artists, trackname and album.

        Args:
            tracks: JSON format of specified playlist.

        Returns:
            df: pandas dataframe of specified playlist

        """
        track_list_ = []
        artists_ = []
        albums_ = []
        id_ = []
        for idx, item in enumerate(tracks["items"]):
            track_detail = item["track"]
            id_.append(track_detail["id"])
            track_list_.append(track_detail["name"])
            artists_.append(track_detail["artists"][0]["name"])
            albums_.append(track_detail["album"]["name"])

        df = pd.DataFrame(
            {
                "track_id": pd.Series(id_),
                "artists": pd.Series(artists_),
                "trackname": pd.Series(track_list_),
                "album": pd.Series(albums_),
            }
        )

        return df

    def get_playlists(self, playlistname):
        """
        Concats playlist into a dataframe.
        Spotify has a limit of 100 tracks with their GET request.

        Args:
            playlistname: specific playlist name

        Returns:
            pl_df: pandas dataframe of specified playlist
        """
        try:
            sp = self.get_connection()
            playlists = sp.user_playlists(self.username)
            for playlist in playlists["items"]:
                if (
                    playlist["owner"]["id"] == self.username
                    and playlist["name"] == playlistname
                ):
                    results = sp.user_playlist(self.username, playlist["id"])
                    tracks = results["tracks"]
                    this_df = self.dataframe_tracks(tracks)
                    over_df = []
                    if len(this_df) == 100:
                        while tracks["next"]:
                            tracks = sp.next(tracks)
                            this_df_n = self.dataframe_tracks(tracks)
                            if len(this_df_n) <= 100:
                                over_df.append(this_df_n)

            if over_df:
                total_df = pd.concat(over_df)
                pl_df = pd.concat([this_df, total_df]).reset_index(drop=True)
            else:
                pl_df = this_df

            pl_df["name_of_playlist"] = playlistname

            return pl_df

        except Exception as e:
            print(f"Failed to get playlist dataframe because of " + str(e))
