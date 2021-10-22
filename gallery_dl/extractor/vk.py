# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vk.com/"""

from .common import Extractor, Message
from .. import text
import re

BASE_PATTERN = r"(?:https://)?(?:www\.|m\.)?vk\.com"


class VkExtractor(Extractor):
    """Base class for vk extractors"""
    category = "vk"
    directory_fmt = ("{category}", "{user[name]|user[id]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://vk.com"
    request_interval = 1.0

    def items(self):
        data = self.metadata()
        yield Message.Directory, data
        for photo in self.photos():
            photo.update(data)
            yield Message.Url, photo["url"], photo

    def _pagination(self, photos_url, user_id):
        sub = re.compile(r"/imp[fg]/").sub
        needle = 'data-id="{}_'.format(user_id)
        cnt = 0

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Origin"          : self.root,
            "Referer"         : photos_url,
        }
        params = {
            "al"    : "1",
            "al_ad" : "0",
            "offset": 0,
            "part"  : "1",
        }

        while True:
            payload = self.request(
                photos_url, method="POST", headers=headers, data=params
            ).json()["payload"][1]

            offset = payload[0]
            html = payload[1]

            for cnt, photo in enumerate(text.extract_iter(html, needle, ')')):
                pid = photo[:photo.find('"')]
                url = photo[photo.rindex("(")+1:]
                url = sub("/", url.partition("?")[0])
                yield text.nameext_from_url(url, {"url": url, "id": pid})

            if cnt <= 20 or offset == params["offset"]:
                return
            params["offset"] = offset


class VkPhotosExtractor(VkExtractor):
    """Extractor for photos from a vk user"""
    subcategory = "photos"
    pattern = (BASE_PATTERN + r"/(?:"
               r"(?:albums|photos|id)(-?\d+)"
               r"|(?!album-?\d+_)([^/?#]+))")
    test = (
        ("https://vk.com/id398982326", {
            "pattern": r"https://sun\d+-\d+\.userapi\.com/c\d+/v\d+"
                       r"/[0-9a-f]+/[\w-]+\.jpg",
            "count": ">= 35",
            "keywords": {
                "id": r"re:\d+",
                "user": {
                    "id": "398982326",
                    "info": "Мы за Движуху! – m1ni SounD #4 [EROmusic]",
                    "name": "",
                    "nick": "Dobrov Kurva",
                },
            },
        }),
        ("https://vk.com/cosplayinrussia", {
            "range": "75-100",
            "keywords": {
                "id": r"re:\d+",
                "user": {
                    "id"  : "-165740836",
                    "info": "Предложка открыта, кидайте ваши косплейчики. При "
                            "правильном оформлении они будут опубликованы",
                    "name": "cosplayinrussia",
                    "nick": "Косплей | Cosplay 18+",
                },
            },
        }),
        ("https://m.vk.com/albums398982326"),
        ("https://www.vk.com/id398982326?profile=1"),
        ("https://vk.com/albums-165740836"),
    )

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id, self.user_name = match.groups()

    def photos(self):
        url = "{}/photos{}".format(self.root, self.user_id)
        return self._pagination(url, self.user_id)

    def metadata(self):
        if self.user_id:
            user_id = self.user_id
            prefix = "public" if user_id[0] == "-" else "id"
            url = "{}/{}{}".format(self.root, prefix, user_id.lstrip("-"))
            data = self._extract_profile(url)
        else:
            url = "{}/{}".format(self.root, self.user_name)
            data = self._extract_profile(url)
            self.user_id = data["user"]["id"]
        return data

    def _extract_profile(self, url):
        extr = text.extract_from(self.request(url).text)
        return {"user": {
            "name": text.unescape(extr(
                'rel="canonical" href="https://vk.com/', '"')),
            "nick": text.unescape(extr(
                '<h1 class="page_name">', "<")).replace("  ", " "),
            "info": text.unescape(text.remove_html(extr(
                '<span class="current_text">', '</span'))),
            "id"  : extr('<a href="/albums', '"'),
        }}


class VkAlbumExtractor(VkExtractor):
    """Extractor for a vk album"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user[id]}", "{album[id]}")
    pattern = BASE_PATTERN + r"/album(-?\d+)_(\d+)$"
    test = (
        ("https://vk.com/album221469416_0", {
            "count": 3,
        }),
        ("https://vk.com/album-165740836_281339889", {
            "count": 12,
        }),
    )

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id, self.album_id = match.groups()

    def photos(self):
        url = "{}/album{}_{}".format(self.root, self.user_id, self.album_id)
        return self._pagination(url, self.user_id)

    def metadata(self):
        return {
            "user": {"id": self.user_id},
            "album": {"id": self.album_id},
        }
