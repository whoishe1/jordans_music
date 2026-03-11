from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
from io import StringIO
from pathlib import Path
import pandas as pd


class LoadData:
    """Loads playlist data into Google Cloud Storage and BigQuery.

    Attributes:
        service_account_path: path to google service account JSON credentials
        scopes: google authorization scopes
        project: name of google project
        bucket_name: name of google storage bucket
    """

    def __init__(self, service_account, googlescopes, project, bucket_name):
        self.service_account_path = service_account
        self.scopes = googlescopes
        self.project = project
        self.bucket_name = bucket_name
        self._credentials = service_account.Credentials.from_service_account_file(
            self.service_account_path, scopes=self.scopes
        )

    def _gcs_client(self):
        return storage.Client(project=self.project, credentials=self._credentials)

    def _bq_client(self):
        return bigquery.Client(project=self.project, credentials=self._credentials)

    def _get_bucket(self):
        return self._gcs_client().bucket(self.bucket_name)

    def to_gcs_spec(self):
        """Upload the most recent spotify and soundcloud CSVs to GCS."""
        bucket = self._get_bucket()

        sources = {
            "spotify": Path("data/spotify"),
            "soundcloud": Path("data/soundcloud"),
        }

        for source, data_dir in sources.items():
            latest_file = max(data_dir.glob("*.csv"), key=lambda p: p.stat().st_mtime)
            blob = bucket.blob(f"{source}/{latest_file.name}")
            blob.upload_from_filename(str(latest_file))

        print("Uploaded specific spotify and soundcloud data")

    # Keep old misspelled name as alias for backwards compatibility with dagster job
    to_gsc_spec = to_gcs_spec

    def gcs_staging(self, type_of_playlist):
        """Merge all historical data for a source and upload as a staging CSV."""
        bucket = self._get_bucket()
        df = self._merge_playlists(type_of_playlist)

        blob = bucket.blob(f"{type_of_playlist}_staging/{type_of_playlist}.csv")
        blob.upload_from_string(df.to_csv(index=False), "text/csv")

        print(f"Uploaded staging {type_of_playlist} data to GCS")

    # Keep old misspelled name as alias for backwards compatibility with dagster job
    gsc_staging = gcs_staging

    def _merge_playlists(self, playlist_type):
        """Read all historical CSVs for a source from GCS and concatenate them."""
        if playlist_type not in ("spotify", "soundcloud"):
            raise ValueError("playlist_type must be 'spotify' or 'soundcloud'")

        prefix = f"{playlist_type}/{playlist_type}"
        client = self._gcs_client()
        bucket = client.bucket(self.bucket_name)

        dfs = []
        for blob in client.list_blobs(self.bucket_name, prefix=prefix):
            date_created = blob.time_created
            data = bucket.blob(blob.name).download_as_bytes()
            df = pd.read_csv(StringIO(data.decode("utf-8")))
            df["date_created"] = date_created
            dfs.append(df)

        return pd.concat(dfs)

    def to_bq(self, schema, dataset_name, table_name, subfolder, name_of_csv):
        """Load a staging CSV from GCS into a BigQuery table (full replace)."""
        client = self._bq_client()

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            skip_leading_rows=1,
            source_format=bigquery.SourceFormat.CSV,
            write_disposition="WRITE_TRUNCATE",
        )

        table_id = f"{self.project}.{dataset_name}.{table_name}"
        uri = f"gs://{self.bucket_name}/{subfolder}/{name_of_csv}.csv"

        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()

        destination_table = client.get_table(table_id)
        print(f"Loaded {destination_table.num_rows} rows.")
