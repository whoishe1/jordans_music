from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
import pathlib
import os
from io import StringIO
import pandas as pd
import datetime


class LoadData:
    """
    loading data into Google Cloud Storage

    Attributes:
        service_account(json): google service account credentials
        googlescopes(list): Spotify authorization scopes, i.e. 'playlist-read-private'
        project: name of google project

    """

    def __init__(self, service_account, googlescopes):
        """
        Credentials for Google
        """

        self.service_account = service_account
        self.googlescopes = googlescopes
        self.project = "jordans-music-343121"
        self.bucket_name = "jordans_music"

    def connect(self, type_of_scope):
        """
        initialize client

        reference: https://developers.google.com/identity/protocols/oauth2
        scope for bigquery is usually: https://www.googleapis.com/auth/bigquery
        scope for cloud storage is usually: https://www.googleapis.com/auth/cloud-platform
        """
        # you must pass a list into the scopes api
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account, scopes=self.googlescopes
        )

        if type_of_scope == "bigquery":
            client = bigquery.Client(project=self.project, credentials=credentials)
        if type_of_scope == "cloud_storage":
            client = storage.Client(project=self.project, credentials=credentials)
        return client

    def to_gsc_spec(self):
        """
        Upload soundcloud and spotify playlists to Google cloud storage on most recent date
        """

        gcs_cred = self.connect(type_of_scope="cloud_storage")

        spotify_df = str(
            max(pathlib.Path(r".\data\spotify").glob("*"), key=os.path.getmtime)
        )
        soundcloud_df = str(
            max(pathlib.Path(r".\data\soundcloud").glob("*"), key=os.path.getmtime)
        )

        dfs = {
            "spotify": spotify_df,
            "soundcloud": soundcloud_df,
        }

        for k, v in dfs.items():
            name_of_file = v.split("\\")[-1]

            bucket = gcs_cred.bucket(self.bucket_name)
            blob = bucket.blob(f"{k}/{name_of_file}")
            blob.upload_from_filename(v)

    def gsc_staging(self, type_of_playlist):
        """
        Staging data to be uploaded in BigQuery
        """

        gcs_cred = self.connect(type_of_scope="cloud_storage")

        bucket = gcs_cred.bucket(self.bucket_name)

        df = self.merge_playlists(type_of_playlist)

        if type_of_playlist == "spotify":
            blob = bucket.blob(f"spotify_staging/spotify.csv")
            blob.upload_from_string(df.to_csv(index=False), "text/csv")
        elif type_of_playlist == "soundcloud":
            blob = bucket.blob(f"soundcloud_staging/soundcloud.csv")
            blob.upload_from_string(df.to_csv(index=False), "text/csv")

    def merge_playlists(self, playlist):
        """
        Reads data from google cloud storage and concats playlist data together, so there will be unique tracks
        """

        if playlist == "soundcloud":
            playlist = "soundcloud/soundcloud"
        elif playlist == "spotify":
            playlist = "spotify/spotify"
        else:
            raise NameError("playlist can only be 'soundcloud' or 'spotify'")

        gcs_cred = self.connect(type_of_scope="cloud_storage")

        bucket = gcs_cred.bucket(self.bucket_name)

        dfs = []
        for blob in gcs_cred.list_blobs(self.bucket_name, prefix=playlist):
            blob = bucket.blob(blob.name)
            data = blob.download_as_bytes()

            s = str(data, "utf-8")
            str_bytes = StringIO(s)

            df = pd.read_csv(str_bytes)
            dfs.append(df)

        all_df = pd.concat(dfs)

        spec_playlist = (
            all_df.sort_values(by=["artists", "trackname"])
            .drop_duplicates()
            .reset_index(drop=True)
        )

        return spec_playlist

    def spotify_staging_to_bq(self):
        """
        Insert raw data into BigQuery from Cloud Storage
        """

        client = self.connect(type_of_scope="bigquery")

        spotify = [
            bigquery.SchemaField("track_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("artists", "STRING"),
            bigquery.SchemaField("trackname", "STRING"),
            bigquery.SchemaField("album", "STRING"),
        ]

        job_config = bigquery.LoadJobConfig(
            schema=spotify,
            skip_leading_rows=1,
            # The source format defaults to CSV, so the line below is optional.
            source_format=bigquery.SourceFormat.CSV,
            write_disposition="WRITE_TRUNCATE",
        )

        table_id = "{self.project}.music.spotify"
        uri = f"gs://{self.bucket_name}/spotify_staging/spotify.csv"

        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)

        load_job.result()

        destination_table = client.get_table(table_id)
        print("Loaded {} rows.".format(destination_table.num_rows))

    def soundcloud_staging_to_bq(self):
        """
        Insert raw data into BigQuery from Cloud Storage
        """

        client = self.connect(type_of_scope="bigquery")

        soundcloud = [
            bigquery.SchemaField("trackname", "STRING"),
            bigquery.SchemaField("artists", "STRING"),
        ]

        job_config = bigquery.LoadJobConfig(
            schema=soundcloud,
            skip_leading_rows=1,
            # The source format defaults to CSV, so the line below is optional.
            source_format=bigquery.SourceFormat.CSV,
            write_disposition="WRITE_TRUNCATE",
        )

        table_id = f"{self.project}.music.soundcloud"
        uri = f"gs://{self.bucket_name}/soundcloud_staging/soundcloud.csv"

        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)

        load_job.result()

        destination_table = client.get_table(table_id)
        print("Loaded {} rows.".format(destination_table.num_rows))
