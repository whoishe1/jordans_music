from util.gcs import LoadData
import pandas as pd
from io import StringIO
import os
from schemas.playlist_schemas import spotify_schema, soundcloud_schema

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

gcs_cred = to_google.connect(type_of_scope="cloud_storage")
bucket = gcs_cred.bucket(to_google.bucket_name)

dfs = []
for blob in gcs_cred.list_blobs(to_google.bucket_name, prefix="soundcloud/soundcloud"):
    print(blob.name)
    date_created = blob.time_created
    print(date_created)
    blob = bucket.blob(blob.name)
    data = blob.download_as_bytes()

    s = str(data, "utf-8")
    str_bytes = StringIO(s)

    df = pd.read_csv(str_bytes)
    df["date_created"] = date_created
    dfs.append(df)
    # print(bucket.blob(blob.time_created))


date_created

# to_google.to_bq(
#     schema=soundcloud_schema,
#     dataset_name="music",
#     table_name="soundcloud",
#     subfolder="soundcloud_staging",
#     name_of_csv="soundcloud",
# )

#
# dfs

all_v = pd.concat(dfs)

# a = bucket.blob("soundcloud_staging/soundcloud.csv")
# a.upload_from_string(all_v.to_csv(index=False), "text/csv")
