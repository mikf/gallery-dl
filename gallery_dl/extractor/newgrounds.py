# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.newgrounds.com/"""

from .common import Extractor, Message
from .. import text
import json


class NewgroundsExtractor(Extractor):
    """Base class for newgrounds extractors"""
    category = "newgrounds"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    archive_fmt = "{index}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.root = "https://{}.newgrounds.com".format(self.user)

    def items(self):
        data = self.metadata()
        yield Message.Version, 1

        for post_url in self.posts():
            file = self.extract_post_data(post_url)
            file.update(data)
            url = file["url"]
            yield Message.Directory, file
            yield Message.Url, url, text.nameext_from_url(url, file)

    def metadata(self):
        """Collect metadata for extractor-job"""
        return {"user": self.user}

    def posts(self):
        """Return urls of all relevant image pages"""

    def extract_post_data(self, post_url):
        """Collect url and metadata from an image post"""
        extr = text.extract_from(self.request(post_url).text)
        full = text.extract_from(json.loads(extr('"full_image_text":', '});')))
        data = {
            "title"      : text.unescape(extr('"og:title" content="', '"')),
            "description": text.unescape(extr(':description" content="', '"')),
            "date"       : text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"')),
            "rating"     : extr('class="rated-', '"'),
            "favorites"  : text.parse_int(extr('id="faves_load">', '<')),
            "score"      : text.parse_float(extr('id="score_number">', '<')),
            "tags"       : text.split_html(extr(
                '<dd class="tags momag">', '</dd>')),
            "url"        : full('src="', '"'),
            "width"      : text.parse_int(full('width="', '"')),
            "height"     : text.parse_int(full('height="', '"')),
        }
        data["tags"].sort()
        data["index"] = text.parse_int(
            data["url"].rpartition("/")[2].partition("_")[0])
        return data

    def _pagination(self, url):
        headers = {
            "Referer": self.root,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        while True:
            data = self.request(url, headers=headers).json()

            for year in data["sequence"]:
                for item in data["years"][str(year)]["items"]:
                    page_url = text.extract(item, 'href="', '"')[0]
                    yield text.urljoin(self.root, page_url)

            if not data["more"]:
                return
            url = text.urljoin(self.root, data["more"])


class NewgroundsUserExtractor(NewgroundsExtractor):
    """Extractor for all images of a newgrounds user"""
    subcategory = "user"
    pattern = r"(?:https?://)?([^.]+)\.newgrounds\.com(?:/art)?/?$"
    test = (
        ("https://blitzwuff.newgrounds.com/art", {
            "url": "24b19c4a135a09889fac7b46a74e427e4308d02b",
            "keyword": "8330e1e563c8a5464938feaceac88aa9870aefe4",
        }),
        ("https://blitzwuff.newgrounds.com/"),
    )

    def posts(self):
        return self._pagination(self.root + "/art/page/1")


class NewgroundsImageExtractor(NewgroundsExtractor):
    """Extractor for a single image from newgrounds.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:www\.)?newgrounds\.com/art/view/([^/?&#]+)/[^/?&#]+"
               r"|art\.ngfiles\.com/images/\d+/\d+_([^_]+)_([^.]+))")
    test = (
        ("https://www.newgrounds.com/art/view/blitzwuff/ffx", {
            "url": "e7778c4597a2fb74b46e5f04bb7fa1d80ca02818",
            "keyword": "3ffcdc8f54a46b8ee1c9b433627f66b750edff51",
            "content": "cb067d6593598710292cdd340d350d14a26fe075",
        }),
        ("https://art.ngfiles.com/images/587000/587551_blitzwuff_ffx.png", {
            "url": "e7778c4597a2fb74b46e5f04bb7fa1d80ca02818",
            "keyword": "3ffcdc8f54a46b8ee1c9b433627f66b750edff51",
        }),
    )

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        if match.group(2):
            self.user = match.group(2)
            self.post_url = "https://www.newgrounds.com/art/view/{}/{}".format(
                self.user, match.group(3))
        else:
            self.post_url = match.group(0)

    def posts(self):
        return (self.post_url,)


class NewgroundsVideoExtractor(NewgroundsExtractor):
    """Extractor for all videos of a newgrounds user"""
    subcategory = "video"
    filename_fmt = "{category}_{index}.{extension}"
    pattern = r"(?:https?://)?([^.]+)\.newgrounds\.com/movies/?$"
    test = ("https://tomfulp.newgrounds.com/movies", {
        "pattern": r"ytdl:https?://www\.newgrounds\.com/portal/view/\d+",
        "count": ">= 32",
    })

    def posts(self):
        return self._pagination(self.root + "/movies/page/1")

    def extract_post_data(self, page_url):
        return {
            "url"  : "ytdl:" + page_url,
            "index": text.parse_int(page_url.rpartition("/")[2]),
        }
