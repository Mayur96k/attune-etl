from google.cloud import storage
from datetime import datetime
import os

from config import (
    BUCKET_NAME,
    REGION,
    SITE
)


def upload_file(local_file, grid_name):

    client = storage.Client()

    bucket = client.bucket(BUCKET_NAME)

    today = datetime.now()

    file_name = os.path.basename(local_file)

    blob_path = (
        f"{REGION}/"
        f"{SITE}/"
        f"{grid_name}/"
        f"{today.year}/"
        f"{today.month:02d}/"
        f"{today.day:02d}/"
        f"{file_name}"
    )

    blob = bucket.blob(blob_path)

    print(f"Uploading to: {blob_path}")

    blob.upload_from_filename(local_file)

    print(f"Uploaded {blob_path}")