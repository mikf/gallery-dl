# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://yiffverse.com/"""

from .booru import BooruExtractor
from .. import text
import collections

BASE_PATTERN = r"(?:https?://)?(?:www\.)?yiffverse\.com"


class YiffverseExtractor(BooruExtractor):
    category = "yiffverse"
    root = "https://yiffverse.com"
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
        params["sortOrder"] = 1
        params["status"] = 2
        params["take"] = self.per_page
        threshold = self.per_page

        while True:
            data = self.request(url, method="POST", json=params).json()

            yield from data["items"]

            if len(data["items"]) < threshold:
                return
            params["cursor"] = data.get("cursor")


class YiffversePostExtractor(YiffverseExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "https://yiffverse.com/post/12345"

    def posts(self):
        return (self._fetch_post(self.groups[0]),)


class YiffversePlaylistExtractor(YiffverseExtractor):
    subcategory = "playlist"
    directory_fmt = ("{category}", "{playlist_id}")
    archive_fmt = "p_{playlist_id}_{id}"
    pattern = BASE_PATTERN + r"/playlist/(\d+)"
    example = "https://yiffverse.com/playlist/12345"

    def metadata(self):
        return {"playlist_id": self.groups[0]}

    def posts(self):
        endpoint = "/v2/post/search/playlist/" + self.groups[0]
        return self._pagination(endpoint)


class YiffverseTagExtractor(YiffverseExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/(?:tag/([^/?#]+))?(?:/?\?([^#]+))?(?:$|#)"
    example = "https://yiffverse.com/tag/TAG"

    def _init(self):
        tag, query = self.groups
        params = text.parse_query(query)

        self.tags = tags = []
        if tag:
            tags.append(text.unquote(tag))
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
