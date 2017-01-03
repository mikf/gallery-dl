# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://luscious.net/"""

from .common import Extractor, Message
from .. import text, iso639_1
from urllib.parse import urljoin
import re

class LusciousAlbumExtractor(Extractor):
    """Extractor for image albums from luscious.net"""
    category = "luscious"
    subcategory = "album"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{num:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?luscious\.net/c/([^/]+)/"
                r"(?:pictures/album|albums)/([^/]+_(\d+))")]
    test = [("https://luscious.net/c/hentai_manga/albums/okinami-no-koigokoro_277031/view/", {
        "url": "7e4984a271a1072ac6483e4228a045895aff86f3",
        "keyword": "f3087f8e5c84e3f52fcd7d672cf0e6beae821837",
        "content": "b3a747a6464509440bd0ff6d1267e6959f8d6ff3",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.section, self.gpart, self.gid = match.groups()

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images():
            image.update(data)
            yield Message.Url, url, image

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        url = "https://luscious.net/c/{}/albums/{}/view/".format(
            self.section, self.gpart)
        page = self.request(url).text
        data, pos = text.extract_all(page, (
            ("title"   , '"og:title" content="', '"'),
            (None      , '<li class="user_info">', ''),
            ("count"   , '<p>', ' '),
            (None      , '<p>Section:', ''),
            ("section" , '>', '<'),
            (None      , '<p>Language:', ''),
            ("language", '', ' '),
            ("artist"  , 'rtist:</strong>\n', '\n'),
        ), values={"gallery-id": self.gid})
        data["lang"] = iso639_1.language_to_code(data["language"])
        data["artist"] = (data["artist"] or "").strip()
        return data

    def get_images(self):
        pnum = 1
        inum = 1
        apiurl = ("https://luscious.net/c/{}/pictures/album/{}/page/{{}}/.json"
                  "/?style=default").format(self.section, self.gpart)
        while True:
            data = self.request(apiurl.format(pnum)).json()
            page = data["html"]
            pos  = 0
            while True:
                imgid, pos = text.extract(page, 'container" id="', '"', pos)
                if not imgid:
                    break
                url  , pos = text.extract(page, 'data-src="', '"', pos)
                title, pos = text.extract(page, 'alt="', '"', pos)
                yield re.sub(r"\.\d+x\d+(\.[a-z]+)$", r"\1", url), {
                    "num": inum,
                    "name": title,
                    "extension": url[url.rfind(".")+1:],
                    "image-id": imgid[8:]
                }
                inum += 1
            if data["paginator_complete"]:
                return
            pnum += 1
