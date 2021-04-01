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
    directory_fmt = ("{category}", "{user[id]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://vk.com"
    request_interval = 1.0
    pattern = r"(?:https://)?(?:www\.|m\.)?vk\.com/(?:albums|photos|id)(\d+)"
    test = (
        ("https://vk.com/id398982326", {
            "pattern": r"https://sun\d+-\d+\.userapi\.com/c\d+/v\d+"
                       r"/[0-9a-f]+/[\w-]+\.jpg",
            "count": ">= 35",
        }),
        ("https://m.vk.com/albums398982326"),
        ("https://www.vk.com/id398982326?profile=1"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id = match.group(1)

    def items(self):
        user_id = self.user_id

        if self.config("metadata"):
            url = "{}/id{}".format(self.root, user_id)
            extr = text.extract_from(self.request(url).text)
            data = {"user": {
                "id"  : user_id,
                "nick": text.unescape(extr(
                    "<title>", " | VK<")),
                "name": text.unescape(extr(
                    '<h1 class="page_name">', "<")).replace("  ", " "),
                "info": text.unescape(text.remove_html(extr(
                    '<span class="current_text">', '</span')))
            }}
        else:
            data = {"user": {"id": user_id}}

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
