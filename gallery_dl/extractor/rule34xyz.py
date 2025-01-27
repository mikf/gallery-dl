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
        0: "general",
        1: "copyright",
        2: "character",
        3: "artist",
    }

    def _init(self):
        formats = self.config("format")
        if formats:
            if isinstance(formats, str):
                formats = formats.split(",")
            self.formats = formats
        else:
            self.formats = ("10", "40", "41", "2")

    def _file_url(self, post):
        post["files"] = files = {
            str(link["type"]): link["url"]
            for link in post.pop("imageLinks")
        }

        for fmt in self.formats:
            if fmt in files:
                break
        else:
            fmt = "2"
            self.log.warning("%s: Requested format not available", post["id"])

        post["file_url"] = url = files[fmt]
        post["format_id"] = fmt
        post["format"] = url.rsplit(".", 2)[1]
        return url

    def _prepare(self, post):
        post.pop("filesPreview", None)
        post.pop("tagsWithType", None)
        post["date"] = text.parse_datetime(
            post["created"][:19], "%Y-%m-%dT%H:%M:%S")

    def _tags(self, post, _):
        if post.get("tagsWithType") is None:
            post.update(self._fetch_post(post["id"]))

        tags = collections.defaultdict(list)
        tagslist = []
        for tag in post["tagsWithType"]:
            value = tag["value"]
            tagslist.append(value)
            tags[tag["type"]].append(value)
        types = self.TAG_TYPES
        for type, values in tags.items():
            post["tags_" + types[type]] = values
        post["tags"] = tagslist

    def _fetch_post(self, post_id):
        url = "{}/api/post/{}".format(self.root, post_id)
        return self.request(url).json()

    def _pagination(self, endpoint, params=None):
        url = "{}/api{}".format(self.root, endpoint)

        if params is None:
            params = {}
        params["IncludeLinks"] = "true"
        params["IncludeTags"] = "true"
        params["OrderBy"] = "0"
        params["Skip"] = self.page_start * self.per_page
        params["Take"] = self.per_page
        params["DisableTotal"] = "true"
        threshold = self.per_page

        while True:
            data = self.request(url, params=params).json()

            yield from data["items"]

            if len(data["items"]) < threshold:
                return
            params["Skip"] += params["Take"]


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
        endpoint = "/playlist-item"
        params = {"PlaylistId": self.groups[0]}
        return self._pagination(endpoint, params)


class Rule34xyzTagExtractor(Rule34xyzExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/([^/?#]+)$"
    example = "https://rule34.xyz/TAG"

    def metadata(self):
        self.tags = text.unquote(self.groups[0]).replace("_", " ")
        return {"search_tags": self.tags}

    def posts(self):
        endpoint = "/post/search"
        params = {"Tag": self.tags}
        return self._pagination(endpoint, params)
