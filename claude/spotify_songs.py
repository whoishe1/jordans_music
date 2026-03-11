import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class GetSpotifyPlaylist:
    """Returns Tracks, Artists, and Album of a specified playlists in a pandas format.

    Attributes:
        username: Spotify username
        scope: Spotify authorization scopes, i.e. 'playlist-read-private'
        client_id: Spotify client id
        client_secret: Spotify client secret
        redirect_uri: redirect authorization url
    """

    def __init__(self, username, scope, client_id, client_secret, redirect_uri=None):
        self.username = username
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
            )
        )

    def my_playlists(self):
        """Returns a list of the current user's playlist names."""
        playlists = self.sp.current_user_playlists(limit=50)
        return [item["name"] for item in playlists["items"]]

    def _parse_tracks(self, tracks):
        """Parse a tracks response page into a list of track dicts."""
        rows = []
        for item in tracks["items"]:
            if item["track"] is None:
                continue
            track = item["track"]
            rows.append(
                {
                    "track_id": track["id"],
                    "artists": track["artists"][0]["name"],
                    "trackname": track["name"],
                    "album": track["album"]["name"],
                }
            )
        return rows

    def get_playlists(self, playlistname):
        """Fetch all tracks for a named playlist, handling Spotify's 100-track pagination.

        Args:
            playlistname: specific playlist name

        Returns:
            pandas DataFrame of the playlist's tracks
        """
        playlists = self.sp.user_playlists(self.username)
        for playlist in playlists["items"]:
            if playlist["owner"]["id"] == self.username and playlist["name"] == playlistname:
                tracks = self.sp.user_playlist(self.username, playlist["id"])["tracks"]
                all_rows = self._parse_tracks(tracks)

                while tracks["next"]:
                    tracks = self.sp.next(tracks)
                    all_rows.extend(self._parse_tracks(tracks))

                df = pd.DataFrame(all_rows)
                df["name_of_playlist"] = playlistname
                return df

        raise ValueError(f"Playlist '{playlistname}' not found for user '{self.username}'")
