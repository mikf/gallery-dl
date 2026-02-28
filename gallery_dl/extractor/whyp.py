# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://whyp.it/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?whyp\.it"


class WhypExtractor(Extractor):
    """Base class for whyp extractors"""
    category = "whyp"
    root = "https://whyp.it"
    root_api = "https://api.whyp.it"
    directory_fmt = ("{category}", "{user[username]} ({user[id]})")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"

    def _init(self):
        self.headers_api = {
            "Accept" : "application/json",
            "Origin" : self.root,
            "Referer": self.root + "/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

    def items(self):
        for track in self.tracks():
            if url := track.get("lossless_url"):
                track["original"] = True
            else:
                url = track["lossy_url"]
                track["original"] = False

            if "created_at" in track:
                track["date"] = self.parse_datetime_iso(track["created_at"])

            yield Message.Directory, "", track
            yield Message.Url, url, text.nameext_from_url(url, track)


class WhypAudioExtractor(WhypExtractor):
    subcategory = "audio"
    pattern = BASE_PATTERN + r"/tracks/(\d+)(?:/[^/?#]+)?/?(?:\?([^#]+))?"
    example = "https://whyp.it/tracks/12345/SLUG"

    def tracks(self):
        tid, qs = self.groups
        url = f"{self.root_api}/api/tracks/{tid}"
        params = None if qs is None else text.parse_query(qs)
        data = self.request_json(url, params=params, headers=self.headers_api)
        return (data["track"],)


class WhypUserExtractor(WhypExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/users/(\d+)(?:/[^/?#]+)?/?(?:\?([^#]+))?"
    example = "https://whyp.it/users/123/NAME"

    def tracks(self):
        uid, qs = self.groups

        url = f"{self.root_api}/api/users/{uid}/tracks"
        params = text.parse_query(qs)
        headers = self.headers_api

        while True:
            data = self.request_json(url, params=params, headers=headers)

            yield from data["tracks"]

            if not (cursor := data.get("next_cursor")):
                break
            params["cursor"] = cursor


class WhypCollectionExtractor(WhypExtractor):
    subcategory = "collection"
    pattern = BASE_PATTERN + r"/collections/(\d+)(?:/[^/?#]+)?/?(?:\?([^#]+))?"
    example = "https://whyp.it/collections/123/NAME"

    def tracks(self):
        cid, qs = self.groups

        url = f"{self.root_api}/api/collections/{cid}"
        params = None if qs is None else text.parse_query(qs)
        headers = self.headers_api
        self.kwdict["collection"] = collection = self.request_json(
            url, params=params, headers=headers)["collection"]

        url = f"{self.root_api}/api/collections/{cid}/tracks"
        params = {"token": collection["token"]}
        data = self.request_json(url, params=params, headers=headers)
        return data["tracks"]
