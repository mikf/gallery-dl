import re
import base64

from .common import Extractor, Message


class CyberdropExtractor(Extractor):
    pattern = r"(?:https?://)?(?:www\.)?cyberdrop\.me/a/([^/]+)/?"
    category = "cyberdrop"
    subcategory = "thread"
    directory_fmt = ("{category}", "{album}")
    root = "https://cyberdrop.me"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)
        self.album_url = self.root + "/a/" + self.album_id

    def items(self):
        initial_page_response = self.request(self.album_url)

        albumNameRegex = r"name: '([^']+)'"
        albumName = re.findall(albumNameRegex, initial_page_response.text)[0]

        fileListRegex = r"fl:.'([^']+)'"
        results = re.findall(fileListRegex, initial_page_response.text)
        if (len(results)) != 1:
            raise RuntimeError("could not find file list in html")

        fileList = [base64.b64decode(s.encode('ascii')).decode('utf8') for s in results[0].split(",")]

        for f in fileList:
            ext = f[f.rindex(".") + 1:]
            name = f[:f.rindex(".")]
            data = {
                "extension": ext,
                "filename": name
            }
            yield Message.Directory, {
                "album": self.album_id + ": " + albumName
            }
            yield Message.Url, "https://f.cyberdrop.cc/" + f, data
