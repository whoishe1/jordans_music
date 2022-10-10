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
        googlescopes(list): google authorization scopes, i.e. 'https://www.googleapis.com/auth/cloud-platform'
        project: name of google project
        bucket_name: name of google storage bucket

    """

    def __init__(self, service_account, googlescopes, project, bucket_name):
        """
        Credentials for Google
        """

        self.service_account = service_account
        self.googlescopes = googlescopes
        self.project = project
        self.bucket_name = bucket_name
        # self.project = "jordans-music-343121"
        # self.bucket_name = "jordans_music"

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
        try:
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

        except Exception as e:
            print(e)

        else:
            print(f"Uploaded specific spotify and soundcloud data")

    def gsc_staging(self, type_of_playlist):
        """
        Staging data to be uploaded in BigQuery
        """

        try:
            gcs_cred = self.connect(type_of_scope="cloud_storage")

            bucket = gcs_cred.bucket(self.bucket_name)

            df = self.merge_playlists(type_of_playlist)

            if type_of_playlist == "spotify":
                blob = bucket.blob(f"spotify_staging/spotify.csv")
                blob.upload_from_string(df.to_csv(index=False), "text/csv")
            elif type_of_playlist == "soundcloud":
                blob = bucket.blob(f"soundcloud_staging/soundcloud.csv")
                blob.upload_from_string(df.to_csv(index=False), "text/csv")

        except Exception as e:
            print("e")

        else:
            print(f"Uploaded staging {type_of_playlist} data to GCS")

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

        # spec_playlist = (
        #     all_df.sort_values(by=["artists", "trackname", "name_of_playlist"])
        #     .drop_duplicates(subset=["artists", "trackname"])
        #     .reset_index(drop=True)
        # )

        return all_df

    def to_bq(self, schema, dataset_name, table_name, subfolder, name_of_csv):
        """
        Insert raw data into BigQuery from Cloud Storage
        """
        try:
            client = self.connect(type_of_scope="bigquery")

            job_config = bigquery.LoadJobConfig(
                schema=schema,
                skip_leading_rows=1,
                # The source format defaults to CSV, so the line below is optional.
                source_format=bigquery.SourceFormat.CSV,
                write_disposition="WRITE_TRUNCATE",
            )

            table_id = f"{self.project}.{dataset_name}.{table_name}"
            uri = f"gs://{self.bucket_name}/{subfolder}/{name_of_csv}.csv"

            load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)

            load_job.result()

            destination_table = client.get_table(table_id)

        except Exception as e:
            print(f"Could not load unfunded data to BigQuery due to {e}")

        else:
            print("Loaded {} rows.".format(destination_table.num_rows))
