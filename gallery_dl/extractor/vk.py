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


class VkPhotosExtractor(Extractor):
    """Extractor for photos from a vk user"""
    category = "vk"
    subcategory = "photos"
    directory_fmt = ("{category}", "{user[name]|user[id]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://vk.com"
    request_interval = 1.0
    pattern = (r"(?:https://)?(?:www\.|m\.)?vk\.com/(?:"
               r"(?:albums|photos|id)(-?\d+)|([^/?#]+))")
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
        Extractor.__init__(self, match)
        self.user_id, self.user_name = match.groups()

    def items(self):
        if self.user_id:
            user_id = self.user_id
            prefix = "public" if user_id[0] == "-" else "id"
            url = "{}/{}{}".format(self.root, prefix, user_id.lstrip("-"))
            data = self._extract_profile(url)
        else:
            url = "{}/{}".format(self.root, self.user_name)
            data = self._extract_profile(url)
            user_id = data["user"]["id"]

        photos_url = "{}/photos{}".format(self.root, user_id)
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

        yield Message.Directory, data
        sub = re.compile(r"/imp[fg]/").sub
        needle = 'data-id="{}_'.format(user_id)
        cnt = 0

        while True:
            offset, html = self.request(
                photos_url, method="POST", headers=headers, data=params
            ).json()["payload"][1]

            for cnt, photo in enumerate(text.extract_iter(html, needle, ')')):
                data["id"] = photo[:photo.find('"')]
                url = photo[photo.rindex("(")+1:]
                url = sub("/", url.partition("?")[0])
                yield Message.Url, url, text.nameext_from_url(url, data)

            if cnt <= 40 or offset == params["offset"]:
                return
            params["offset"] = offset

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
