import os
import redis
import lzma
import requests
import shutil
import datetime
import json
import threading

from download import download
from movielistparser import MovieListParser

movie_url = os.environ["MOVIE_LIST_URL"] if "MOVIE_LIST_URL" in os.environ else "https://liste.mediathekview.de/Filmliste-akt.xz"
timestamp_key = "midxer:timestamp"


class Mediathek():
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost', port=6379, decode_responses=True
        )

        timestamp = self.redis.get(
            'midxer:timestamp'
        )

        if timestamp is None:
            download_thread = threading.Thread(
                target=self.update_list, name="Downloader", args=[self.redis])
            download_thread.start()

    def get_movies(self):
        keys = self.redis.keys("midxer:entry:[0-9]")

        for key in keys:
            yield self.redis.hgetall(key)

    @staticmethod
    def update_list(redis):
        print("Starting import...")
        download_name = "data/Filmliste-akt.xz"
        target_file = "data/movie_list.json"

        if download(url=movie_url, target_name=download_name):
            if os.path.isfile(target_file):
                os.remove(target_file)

        if not os.path.isfile(target_file):
            with lzma.open(download_name, 'r') as archive, open(target_file, "wb") as output:
                print("Decompressing downloaded file...")
                shutil.copyfileobj(archive, output)

        parser = MovieListParser(target_file)
        # TODO uncomment when parser is working
        # self.redis.set(timestamp_key, datetime.datetime.now())
        numentries = 0
        for entry in parser.parse():
            numentries += 1

            if numentries > 10000:
                break

            redis.hmset(f"midxer:entry:{numentries}", entry)

        redis.set('midxer:timestamp', datetime.datetime.now().ctime())

        print(f"Import of {numentries} entries done!")
