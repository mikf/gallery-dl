# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34.xyz/"""

from .booru import BooruExtractor
from .. import text
import collections

BASE_PATTERN = r"(?:https?://)?rule34\.xyz"


class Rule34xyzExtractor(BooruExtractor):
    category = "rule34xyz"
    root = "https://rule34.xyz"
    root_cdn = "https://rule34xyz.b-cdn.net"
    filename_fmt = "{category}_{id}.{extension}"
    per_page = 60

    TAG_TYPES = {
        None: "general",
        0   : "general",
        1   : "general",
        2   : "copyright",
        4   : "character",
        8   : "artist",
    }
    FORMATS = {
        "10" : "pic.jpg",
        "100": "mov.mp4",
        "101": "mov720.mp4",
        "102": "mov480.mp4",
    }

    def _init(self):
        formats = self.config("format")
        if formats:
            if isinstance(formats, str):
                formats = formats.split(",")
            self.formats = formats
        else:
            self.formats = ("100", "101", "102", "10")

    def _file_url(self, post):
        files = post["files"]

        for fmt in self.formats:
            if fmt in files:
                extension = self.FORMATS.get(fmt)
                break
        else:
            self.log.warning("%s: Requested format not available", post["id"])
            fmt = next(iter(files))

        post_id = post["id"]
        root = self.root_cdn if files[fmt][0] else self.root
        post["file_url"] = url = "{}/posts/{}/{}/{}.{}".format(
            root, post_id // 1000, post_id, post_id, extension)
        post["format_id"] = fmt
        post["format"] = extension.partition(".")[0]

        return url

    def _prepare(self, post):
        post.pop("files", None)
        post["date"] = text.parse_datetime(
            post["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
        post["filename"], _, post["format"] = post["filename"].rpartition(".")
        if "tags" in post:
            post["tags"] = [t["value"] for t in post["tags"]]

    def _tags(self, post, _):
        if "tags" not in post:
            post.update(self._fetch_post(post["id"]))

        tags = collections.defaultdict(list)
        for tag in post["tags"]:
            tags[tag["type"]].append(tag["value"])
        types = self.TAG_TYPES
        for type, values in tags.items():
            post["tags_" + types[type]] = values

    def _fetch_post(self, post_id):
        url = "{}/api/v2/post/{}".format(self.root, post_id)
        return self.request(url).json()

    def _pagination(self, endpoint, params=None):
        url = "{}/api{}".format(self.root, endpoint)

        if params is None:
            params = {}
        params["Skip"] = self.page_start * self.per_page
        params["take"] = self.per_page
        params["CountTotal"] = False
        params["IncludeLinks"] = True
        params["OrderBy"] = 0
        threshold = self.per_page

        while True:
            data = self.request(url, method="POST", json=params).json()

            yield from data["items"]

            if len(data["items"]) < threshold:
                return
            params["Skip"] += self.per_page
            params["cursor"] = data["cursor"]


class Rule34xyzPostExtractor(Rule34xyzExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "https://rule34.xyz/post/12345"

    def posts(self):
        return (self._fetch_post(self.groups[0]),)


class Rule34xyzPlaylistExtractor(Rule34xyzExtractor):
    subcategory = "playlist"
    directory_fmt = ("{category}", "{playlist_id}")
    archive_fmt = "p_{playlist_id}_{id}"
    pattern = BASE_PATTERN + r"/playlists/view/(\d+)"
    example = "https://rule34.xyz/playlists/view/12345"

    def metadata(self):
        return {"playlist_id": self.groups[0]}

    def posts(self):
        endpoint = "/v2/post/search/playlist/" + self.groups[0]
        return self._pagination(endpoint)


class Rule34xyzTagExtractor(Rule34xyzExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/([^/?#]+)$"
    example = "https://rule34.xyz/TAG"

    def metadata(self):
        self.tags = text.unquote(text.unquote(
            self.groups[0]).replace("_", " ")).split("|")
        return {"search_tags": ", ".join(self.tags)}

    def posts(self):
        endpoint = "/v2/post/search/root"
        params = {"includeTags": self.tags}
        return self._pagination(endpoint, params)
