# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://furry34.com/"""

from .booru import BooruExtractor
from .. import text
import collections

BASE_PATTERN = r"(?:https?://)?(?:www\.)?furry34\.com"


class Furry34Extractor(BooruExtractor):
    category = "furry34"
    root = "https://furry34.com"
    root_cdn = "https://furry34com.b-cdn.net"
    filename_fmt = "{category}_{id}.{extension}"
    per_page = 30

    TAG_TYPES = {
        None: "general",
        1   : "general",
        2   : "copyright",
        4   : "character",
        8   : "artist",
    }
    FORMATS = (
        ("100", "mov.mp4"),
        ("101", "mov720.mp4"),
        ("102", "mov480.mp4"),
        ("10" , "pic.jpg"),
    )

    def _file_url(self, post):
        files = post["files"]
        for fmt, extension in self.FORMATS:
            if fmt in files:
                break
        else:
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
            tags[tag["type"] or 1].append(tag["value"])
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
        params["sortBy"] = 0
        params["take"] = self.per_page
        threshold = self.per_page

        while True:
            data = self.request(url, method="POST", json=params).json()

            yield from data["items"]

            if len(data["items"]) < threshold:
                return
            params["cursor"] = data.get("cursor")


class Furry34PostExtractor(Furry34Extractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "https://furry34.com/post/12345"

    def posts(self):
        return (self._fetch_post(self.groups[0]),)


class Furry34PlaylistExtractor(Furry34Extractor):
    subcategory = "playlist"
    directory_fmt = ("{category}", "{playlist_id}")
    archive_fmt = "p_{playlist_id}_{id}"
    pattern = BASE_PATTERN + r"/playlists/view/(\d+)"
    example = "https://furry34.com/playlists/view/12345"

    def metadata(self):
        return {"playlist_id": self.groups[0]}

    def posts(self):
        endpoint = "/v2/post/search/playlist/" + self.groups[0]
        return self._pagination(endpoint)


class Furry34TagExtractor(Furry34Extractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/(?:([^/?#]+))?(?:/?\?([^#]+))?(?:$|#)"
    example = "https://furry34.com/TAG"

    def _init(self):
        tag, query = self.groups
        params = text.parse_query(query)

        self.tags = tags = []
        if tag:
            tags.extend(text.unquote(text.unquote(tag)).split("|"))
        if "tags" in params:
            tags.extend(params["tags"].split("|"))

        type = params.get("type")
        if type == "video":
            self.type = 1
        elif type == "image":
            self.type = 0
        else:
            self.type = None

    def metadata(self):
        return {"search_tags": " ".join(self.tags)}

    def posts(self):
        endpoint = "/v2/post/search/root"
        params = {"includeTags": [t.replace("_", " ") for t in self.tags]}
        if self.type is not None:
            params["type"] = self.type
        return self._pagination(endpoint, params)
