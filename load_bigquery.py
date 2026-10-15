import json
import csv
from pathlib import Path
from datetime import datetime

import pandas as pd
from google.cloud import bigquery

from config import (
    PROJECT_ID,
    REGION,
    SITE
)

from table_mapping import GRID_CONFIG


# =======================================
# CONFIGURATION
# =======================================

DATASET_ID = "attune_raw"

client = bigquery.Client(
    project=PROJECT_ID
)

# =======================================
# PROCESS ALL GRIDS
# =======================================

for grid_name, config in GRID_CONFIG.items():

    print("\n" + "=" * 60)
    print(f"Processing Grid: {grid_name}")
    print("=" * 60)

    files = sorted(
        Path("data").glob(f"{grid_name}_*.json"),
        reverse=True
    )

    if not files:
        print(f"No file found for {grid_name}")
        continue

    json_file = files[0]

    print(f"Using file: {json_file}")

    # =======================================
    # READ JSON
    # =======================================

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    result_data = data["Result"]["ResultData"]

    # =======================================
    # FIND HEADER
    # =======================================

    header_pos = result_data.rfind(
        config["header"]
    )

    if header_pos == -1:
        raise Exception(
            f"Header not found for {grid_name}"
        )

    data_section = result_data[:header_pos]

    header_section = result_data[header_pos:]

    header_lines = header_section.splitlines()

    header = [
        col.strip().upper()
        for col in header_lines[0].split(",")
    ]

    print(f"Columns Found: {len(header)}")

    # =======================================
    # PARSE DATA
    # =======================================

    records = []

    reader = csv.reader(
        data_section.splitlines()
    )

    for row in reader:

        if not row:
            continue

        if len(row) < len(header):
            row.extend(
                [""] * (len(header) - len(row))
            )

        if len(row) > len(header):
            row = row[:len(header)]

        records.append(row)

    print(f"Rows Found: {len(records)}")

    # =======================================
    # CREATE DATAFRAME
    # =======================================

    df = pd.DataFrame(
        records,
        columns=header
    )

    # =======================================
    # ADD METADATA COLUMNS
    # =======================================

    df["REGION"] = REGION
    df["SITE"] = SITE
    df["SOURCE_GRID"] = grid_name
    df["SOURCE_FILE"] = json_file.name
    df["LOAD_TIMESTAMP"] = datetime.utcnow()

    print("\nSample Data:")
    print(df.head())

    # =======================================
    # BIGQUERY TARGET
    # =======================================

    table_id = (
        f"{PROJECT_ID}."
        f"{DATASET_ID}."
        f"{config['table']}"
    )

    print(f"\nLoading table: {table_id}")

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config
    )

    job.result()

    print(
        f"SUCCESS: Loaded {len(df)} rows "
        f"into {table_id}"
    )

print("\nAll grids processed successfully.")