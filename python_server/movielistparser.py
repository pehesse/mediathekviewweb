import re
import json


class MovieListParser():
    def __init__(self, file):
        self.file = file
        self.pos = 0
        self.unprocessed = ""

    def __read_chunks(self, file_object, chunk_size=4096):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            self.pos += len(data)

            if not data:
                break

            yield data

    def parse(self):
        with open(self.file, "r") as f:
            f.seek(self.pos)
            search_metadata = True
            metadata = []

            for chunk in self.__read_chunks(f):
                if search_metadata:
                    splitted = re.split(r'"Filmliste":|,"X":', chunk)

                    # It should be the third entry
                    if len(splitted) >= 3 and splitted[2].startswith('["Sender",'):
                        metadata = json.loads(splitted[2])
                        search_metadata = False
                    else:
                        print(f"Could not find meta data entry in \n\n{chunk}")
                        return

                pattern = re.compile(r',"X":(.*?)]')
                matches = pattern.finditer(chunk)

                for match in matches:
                    # print(match.start(), match.group())
                    f.seek(match.start() + len(match.group()))
                    yield dict(zip(metadata, json.loads(re.split(r'"X":', match.group())[1])))
