from .common import Extractor, Message
from .. import text


class ZzzzAlbumExtractor(Extractor):
    category = "zzzz"
    subcategory = "album"
    pattern = r"(?:https?://)?zz\.(ht|fo)/a/([^/?#]+)"
    root = "https://zz.ht"
    directory_fmt = ("{category}", "{album_name} ({album_id})")
    test = (
        ("https://zz.ht/a/lop7W6EZ", {
            "pattern": "https://z.zz.fo/.*",
            "keyword": {"album_id": "lop7W6EZ", "album_name": "ferris"}
        }),
        ("https://zz.fo/a/lop7W6EZ", {
            "pattern": "https://z.zz.fo/.*",
            "keyword": {"album_id": "lop7W6EZ", "album_name": "ferris"}
        })
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(2)

    def items(self):
        url = self.root + "/a/" + self.album_id
        extr = text.extract_from(self.request(url).text, default=None)
        album_name = extr("<title>", "</title>")
        files = []
        while True:
            url = extr('class="image" href="', '"')
            if not url:
                break
            files.append(text.unescape(url))
        data = {
            "album_id": self.album_id,
            "album_name": album_name
        }
        yield Message.Directory, data
        for url in files:
            text.nameext_from_url(url, data)
            yield Message.Url, url, data
