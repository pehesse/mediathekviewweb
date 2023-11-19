import sys
import requests
import os
from datetime import datetime


def get_timestamp_from_header(input: str):
    last_updated_pattern = "%a, %d %b %Y %H:%M:%S %Z"
    return int(datetime.strptime(input, last_updated_pattern).timestamp())
    # return os.utime(input, (timestamp, timestamp))


def download(url: str, target_name: str):
    print(f"Downloading {url} to {target_name}")

    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')
    last_modified = get_timestamp_from_header(
        response.headers.get('last-modified'))

    if os.path.isfile(target_name):
        file_date = os.path.getctime(target_name)

        if file_date >= last_modified:
            print("File did already exist and was newer...")
            print("Skipping download!")
            return False

    with open(target_name, "wb") as f:
        if total_length is None:  # no content length header
            print("No content-length was set. Downloading unknown size...")
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)))
                sys.stdout.flush()

            print("\t\t\t - Done!")

    return True
