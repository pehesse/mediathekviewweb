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
from enum import Enum

movie_url = os.environ["MOVIE_LIST_URL"] if "MOVIE_LIST_URL" in os.environ else "https://liste.mediathekview.de/Filmliste-akt.xz"
timestamp_key = "midxer:timestamp"

MediathekState = Enum(
    "MediathekState", "INIT STARTED DOWNLOADING PARSING ERROR_DOWNLOAD ERROR_PARSING"
)


class Mediathek():
    def __init__(self):
        self.state = MediathekState.INIT
        self.entrycount = 0
        self.redis = redis.Redis(
            host='localhost', port=6379, decode_responses=True
        )

        timestamp = self.redis.get(
            'midxer:timestamp'
        )

        if timestamp is None:
            download_thread = threading.Thread(
                target=self.update_list, name="Downloader", args=[self, self.redis])
            download_thread.start()

        self.state = MediathekState.STARTED

    def get_movies(self):
        metadata = json.loads(self.redis.get("midxer:fields"))

        keys = self.redis.keys("midxer:entry:[0-9]")

        for key in keys:
            yield dict(zip(metadata, json.loads(self.redis.get(key))))

    @staticmethod
    def update_list(mediathek, redis):
        print("Starting import...")
        download_name = "data/Filmliste-akt.xz"
        target_file = "data/movie_list.json"

        mediathek.state = MediathekState.DOWNLOADING

        if download(url=movie_url, target_name=download_name):
            if os.path.isfile(target_file):
                os.remove(target_file)

        if not os.path.isfile(target_file):
            with lzma.open(download_name, 'r') as archive, open(target_file, "wb") as output:
                print("Decompressing downloaded file...")
                shutil.copyfileobj(archive, output)

        mediathek.state = MediathekState.PARSING

        parser = MovieListParser(target_file)
        # TODO uncomment when parser is working
        # self.redis.set(timestamp_key, datetime.datetime.now())
        for entry in parser.parse():
            if "Fields" in entry and not isinstance(entry, str):
                # we have the metadata entry
                redis.set("midxer:fields", entry["Fields"])
            else:
                mediathek.entrycount += 1
                redis.set(f"midxer:entry:{mediathek.entrycount}", entry)

        redis.set('midxer:timestamp', datetime.datetime.now().ctime())

        mediathek.state = MediathekState.STARTED
        print(f"Import of {mediathek.entrycount} entries done!")
