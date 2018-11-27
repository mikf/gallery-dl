# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
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
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{category}_{index}_{title}.{extension}"
    archive_fmt = "{index}"

    def __init__(self, match):
        Extractor.__init__(self)
        self.user = match.group(1)
        self.root = "https://{}.newgrounds.com".format(self.user)

    def items(self):
        data = self.get_metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        for page_url in self.get_page_urls():
            url, image = self.parse_page_data(page_url)
            image.update(data)
            yield Message.Url, url, text.nameext_from_url(url, image)

    def get_metadata(self):
        """Collect metadata for extractor-job"""
        return {"user": self.user}

    def get_page_urls(self):
        """Return urls of all relevant image pages"""

    def parse_page_data(self, page_url):
        """Collect url and metadata from an image page"""

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
    pattern = [r"(?:https?://)?([^.]+)\.newgrounds\.com(?:/art)?/?$"]
    test = [
        ("https://blitzwuff.newgrounds.com/art", {
            "url": "24b19c4a135a09889fac7b46a74e427e4308d02b",
            "keyword": "7cbadd5426b8cba270995fffca2e52571d1f9c8d",
        }),
        ("https://derpixon.newgrounds.com/art", None),
        ("https://derpixon.newgrounds.com/", None),
    ]

    def get_page_urls(self):
        return self._pagination(self.root + "/art/page/1")

    def parse_page_data(self, page_url):
        page = self.request(page_url).text

        full, pos = text.extract(page, '"full_image_text":', '});')
        desc, pos = text.extract(page, '"og:description" content="', '"', pos)
        rate, pos = text.extract(page, 'class="rated-', '"', pos)
        tags, pos = text.extract(page, '<dd class="tags momag">', '</dd>', pos)

        full = json.loads(full)
        url   , pos = text.extract(full, 'src="', '"')
        title , pos = text.extract(full, 'alt="', '"', pos)
        width , pos = text.extract(full, 'width="', '"', pos)
        height, pos = text.extract(full, 'height="', '"', pos)

        return url, {
            "title": title,
            "description": text.unescape(desc),
            "width": text.parse_int(width),
            "height": text.parse_int(height),
            "index": text.parse_int(url.rpartition("/")[2].partition("_")[0]),
            "tags": text.split_html(tags),
            "rating": rate,
        }


class NewgroundsImageExtractor(NewgroundsUserExtractor):
    """Extractor for a single image from newgrounds.com"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?newgrounds\.com"
               r"/art/view/([^/?&#]+)/[^/?&#]+"]
    test = [("https://www.newgrounds.com/art/view/blitzwuff/ffx", {
        "url": "e7778c4597a2fb74b46e5f04bb7fa1d80ca02818",
        "keyword": "8f36f33e400016c25dc1be6476a4c1b34881ac86",
        "content": "cb067d6593598710292cdd340d350d14a26fe075",
    })]

    def __init__(self, match):
        NewgroundsUserExtractor.__init__(self, match)
        self.page_url = match.group(0)

    def get_page_urls(self):
        return (self.page_url,)


class NewgroundsVideoExtractor(NewgroundsExtractor):
    """Extractor for all videos of a newgrounds user"""
    subcategory = "video"
    filename_fmt = "{category}_{index}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.newgrounds\.com/movies/?$"]
    test = [("https://twistedgrim.newgrounds.com/movies", {
        "url": "1d72ad0fc7da77135135367b75b777c54c9b18cb",
    })]

    def get_page_urls(self):
        return self._pagination(self.root + "/movies/page/1")

    def parse_page_data(self, page_url):
        return "ytdl:" + page_url, {
            "index": text.parse_int(page_url.rpartition("/")[2])
        }
