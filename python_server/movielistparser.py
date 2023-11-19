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
        with open(self.file, "r", encoding="ISO-8859-1") as f:
            f.seek(self.pos)
            search_metadata = True

            for chunk in self.__read_chunks(f):
                if search_metadata:
                    splitted = re.split(r'"Filmliste":|,"X":', chunk)

                    # It should be the third entry
                    if len(splitted) >= 3 and splitted[2].startswith('["Sender",'):
                        yield {
                            "Fields": splitted[2]
                        }

                        search_metadata = False
                    else:
                        print(f"Could not find meta data entry in \n\n{chunk}")
                        return

                pattern = re.compile(r',"X":(.*?)]')
                matches = pattern.finditer(chunk)

                had_entry = False

                for match in matches:
                    had_entry = True
                    # print(match.start(), match.group())
                    f.seek(f.tell() + match.start() + len(match.group()))
                    yield re.split(r'"X":', match.group())[1]

                if had_entry is False:
                    break
