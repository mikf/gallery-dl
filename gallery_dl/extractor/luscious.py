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
        "url": "f26ec88844a053dba598c213ea7185ecb6b4566a",
        "keyword": "b9281277ab062d95ed0713ea88ed15569d29bf84",
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
        data = text.extract_all(self.request(url).text, (
            ("title"   , '"og:title" content="', '"'),
            (None      , '<li class="user_info">', ''),
            ("count"   , '<p>', ' '),
            (None      , '<p>Section:', ''),
            ("section" , '>', '<'),
            (None      , '<p>Language:', ''),
            ("language", '\n                            ', ' '),
            ("artist"  , 'rtist: ', '\n'),
        ), values={"gallery-id": self.gid})[0]
        data["lang"] = iso639_1.language_to_code(data["language"])
        return data

    def get_images(self):
        """Collect image-urls and -metadata"""
        pnum = 1
        inum = 1
        apiurl = ("https://luscious.net/c/{}/pictures/album/{}/"
                  "page/{{}}/.json/").format(self.section, self.gpart)
        while True:
            data = self.request(apiurl.format(pnum)).json()
            for doc in data["documents"]:
                width, height, size, url = doc["sizes"][-1]
                if size != "original":
                    url = re.sub(r"\.\d+x\d+(\.[a-z]+)$", r"\1", url)
                yield urljoin("https:", url), {
                    "width": width,
                    "height": height,
                    "num": inum,
                    "name": doc["title"],
                    "extension": url[url.rfind(".")+1:],
                }
                inum += 1
            if data["paginator_complete"]:
                return
            pnum += 1
