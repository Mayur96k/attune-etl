import requests
import urllib3
import json

urllib3.disable_warnings()

PAGE_SIZE = 10000

def get_grid_data(config, grid_name):

    url = (
        f"{config['base_url'].rstrip('/')}"
        "/axis/restservices/csvgrids"
    )

    headers = {
        "X-API-Key": config["api_key"],
        "tenant": config["tenant"],
        "organization": config["organization"],
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    cursor_position = 1

    all_rows = []
    metadata = None
    page = 1

    while True:

        print(
            f"Fetching Page {page} "
            f"(Cursor={cursor_position})"
        )

        payload = {
            "GRID_TYPE": {
                "TYPE": "LIST"
            },
            "GRID": {
                "CURRENT_TAB_NAME": "LST",
                "GRID_NAME": grid_name,
                "USER_FUNCTION_NAME": grid_name,
                "NUMBER_OF_ROWS_FIRST_RETURNED": str(PAGE_SIZE),
                "CURSOR_POSITION": str(cursor_position)
            },
            "REQUEST_TYPE": "LIST.HEAD_DATA.STORED"
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False,
            timeout=300
        )

        response.raise_for_status()

        page_json = response.json()

        result_data = page_json["Result"]["ResultData"]

        marker_pos = result_data.rfind("GRIDLABEL")

        if marker_pos == -1:
            raise Exception(
                f"GRIDLABEL section not found for {grid_name}"
            )

        # Actual data
        data_part = result_data[:marker_pos]

        rows = [
            row
            for row in data_part.splitlines()
            if row.strip()
        ]

        print(
            f"Rows fetched on page {page}: "
            f"{len(rows)}"
        )

        all_rows.extend(rows)

        # Metadata section
        meta_part = result_data[marker_pos:]

        metadata_lines = meta_part.splitlines()

        if len(metadata_lines) < 2:
            break

        metadata_row = metadata_lines[1]

        metadata = metadata_row.split(",")

        try:
            current_cursor = metadata[1]
            next_cursor = metadata[2]
            total_records = metadata[3]

            print(
                f"Current Cursor: {current_cursor}"
            )

            print(
                f"Next Cursor: {next_cursor}"
            )

            print(
                f"Records: {total_records}"
            )

        except Exception:
            break

        # Last page
        if (
            not next_cursor
            or next_cursor == current_cursor
        ):
            break

        cursor_position = int(next_cursor)

        page += 1

    # Build final ResultData

    final_result_data = ""

    if metadata_lines:

        header_lines = metadata_lines[2:]

        final_result_data = (
            "\r\n".join(all_rows)
            + "\r\n"
            + "\r\n".join(header_lines)
        )

    page_json["Result"]["ResultData"] = (
        final_result_data
    )

    print(
        f"\nTotal Rows Retrieved: "
        f"{len(all_rows)}"
    )

    return page_json