# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://audiochan.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?audiochan\.com"


class AudiochanExtractor(Extractor):
    """Base class for audiochan extractors"""
    category = "audiochan"
    root = "https://audiochan.com"
    root_api = "https://api.audiochan.com"
    directory_fmt = ("{category}", "{user[display_name]}")
    filename_fmt = "{title} ({slug}).{extension}"
    archive_fmt = "{audioFile[id]}"

    def _init(self):
        self.headers_api = {
            "content-type"   : "application/json",
            "Origin"         : self.root,
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-site",
        }
        self.headers_dl = {
            "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,"
                      "application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
            #  "Range"          : "bytes=0-",
            "Sec-Fetch-Dest" : "audio",
            "Sec-Fetch-Mode" : "no-cors",
            "Sec-Fetch-Site" : "same-site",
            "Accept-Encoding": "identity",
        }

    def items(self):
        for post in self.posts():
            file = post["audioFile"]

            post["_http_headers"] = self.headers_dl
            post["date"] = self.parse_datetime_iso(file["created_at"])
            post["date_updated"] = self.parse_datetime_iso(file["updated_at"])
            post["tags"] = [f"{tag['category']}:{tag['name']}"
                            for tag in post["tags"]]

            yield Message.Directory, post
            text.nameext_from_name(file["filename"], post)
            yield Message.Url, file["url"] or file["stream_url"], post

    def request_api(self, endpoint, params=None):
        url = self.root_api + endpoint
        return self.request_json(url, params=params, headers=self.headers_api)

    def _pagination(self, endpoint, params):
        params["page"] = 1
        params["limit"] = "12"

        while True:
            data = self.request_api(endpoint, params)

            yield from data["data"]

            if not data["has_more"]:
                break
            params["page"] += 1


class AudiochanAudioExtractor(AudiochanExtractor):
    subcategory = "audio"
    pattern = rf"{BASE_PATTERN}/a/(\w+)"
    example = "https://audiochan.com/a/SLUG"

    def posts(self):
        audio = self.request_api("/audios/slug/" + self.groups[0])
        audio["user"] = audio["credits"][0]["user"]
        return (audio,)


class AudiochanUserExtractor(AudiochanExtractor):
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/u/(\w+)"
    example = "https://audiochan.com/u/USER"

    def posts(self):
        endpoint = "/users/" + self.groups[0]
        self.kwdict["user"] = self.request_api(endpoint)["data"]

        params = {
            "sfw_only": "false",
            "sort"    : "new",
        }
        return self._pagination(endpoint + "/audios", params)


class AudiochanCollectionExtractor(AudiochanExtractor):
    subcategory = "collection"
    pattern = rf"{BASE_PATTERN}/c/(\w+)"
    example = "https://audiochan.com/c/SLUG"

    def posts(self):
        slug = self.groups[0]
        endpoint = "/collections/" + slug
        self.kwdict["collection"] = col = self.request_api(endpoint)
        col.pop("audios", None)

        endpoint = f"/collections/slug/{slug}/items"
        return self._pagination(endpoint, {})
