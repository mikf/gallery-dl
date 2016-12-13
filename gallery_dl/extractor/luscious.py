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
        "keyword": "026f4dc2e17aa59f97c9b9d8e68fc52b7c900603",
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
            ("language", '\n                            ', ' '),
            ("artist"  , 'rtist: ', '\n'),
        ), values={"gallery-id": self.gid})
        data["lang"] = iso639_1.language_to_code(data["language"])
        _, pos = text.extract(page, 'ic_container', '')
        self.imageurl = text.extract(page, '<a href="', '"', pos)[0]
        return data

    def get_images(self):
        """Collect image-urls and -metadata"""
        url = self.imageurl
        num = 1
        while True:
            page = self.request(urljoin("https://luscious.net", url)).text
            url, pos = text.extract(page, '<link rel="next" href="', '"')
            data = text.extract_all(page, (
                (None    , '<img id="single_picture"', ''),
                ("width" , 'width="', '"'),
                ("height", 'height="', '"'),
                ("name"  , 'title="', '"'),
                (None    , 'image_option_icons', ''),
                (None    , '<a href="', '"'),
                ("image" , '<a href="', '"'),
            ), pos, values={"num": num})[0]
            image = data["image"]
            data["extension"] = image[image.rfind(".")+1:]
            yield urljoin("https:", image), data
            if url.startswith("/c/-/"):
                return
            num += 1
