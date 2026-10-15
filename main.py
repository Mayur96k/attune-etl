import json
import os
import subprocess
from datetime import datetime

from config import CONFIG
from grids import GRIDS
from extract_attune import get_grid_data
from upload_gcs import upload_file
import sys

print(GRIDS)

os.makedirs("data", exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for grid in GRIDS:

    print(f"\nExtracting {grid}")

    data = get_grid_data(CONFIG, grid)

    file_name = f"{grid}_{timestamp}.json"

    file_path = os.path.join(
        "data",
        file_name
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )

    print(f"Saved {file_path}")

    upload_file(
        file_path,
        grid
    )

print("\nLoading BigQuery tables...")

subprocess.run(
    [sys.executable, os.path.abspath("load_bigquery.py")],
    check=True
)

print("\nPipeline completed successfully.")
