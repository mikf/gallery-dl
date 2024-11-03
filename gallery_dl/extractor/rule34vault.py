# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34vault.com/"""

from .booru import BooruExtractor
from .. import text
import collections

BASE_PATTERN = r"(?:https?://)?rule34vault\.com"


class Rule34vaultExtractor(BooruExtractor):
    category = "rule34vault"
    root = "https://rule34vault.com"
    root_cdn = "https://r34xyz.b-cdn.net"
    filename_fmt = "{category}_{id}.{extension}"
    per_page = 100

    TAG_TYPES = {
        1: "general",
        2: "copyright",
        4: "character",
        8: "artist",
    }

    def _file_url(self, post):
        post_id = post["id"]
        extension = "jpg" if post["type"] == 0 else "mp4"
        post["file_url"] = url = "{}/posts/{}/{}/{}.{}".format(
            self.root_cdn, post_id // 1000, post_id, post_id, extension)
        return url

    def _prepare(self, post):
        post.pop("files", None)
        post["date"] = text.parse_datetime(
            post["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
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
        params["CountTotal"] = False
        params["Skip"] = self.page_start * self.per_page
        params["take"] = self.per_page
        threshold = self.per_page

        while True:
            data = self.request(url, method="POST", json=params).json()

            yield from data["items"]

            if len(data["items"]) < threshold:
                return
            params["cursor"] = data.get("cursor")
            params["Skip"] += params["take"]


class Rule34vaultPostExtractor(Rule34vaultExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "https://rule34vault.com/post/12345"

    def posts(self):
        return (self._fetch_post(self.groups[0]),)


class Rule34vaultPlaylistExtractor(Rule34vaultExtractor):
    subcategory = "playlist"
    directory_fmt = ("{category}", "{playlist_id}")
    archive_fmt = "p_{playlist_id}_{id}"
    pattern = BASE_PATTERN + r"/playlists/view/(\d+)"
    example = "https://rule34vault.com/playlists/view/12345"

    def metadata(self):
        return {"playlist_id": self.groups[0]}

    def posts(self):
        endpoint = "/v2/post/search/playlist/" + self.groups[0]
        return self._pagination(endpoint)


class Rule34vaultTagExtractor(Rule34vaultExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/(?!p(?:ost|laylists)/)([^/?#]+)"
    example = "https://rule34vault.com/TAG"

    def metadata(self):
        self.tags = text.unquote(self.groups[0]).split("%7C")
        return {"search_tags": " ".join(self.tags)}

    def posts(self):
        endpoint = "/v2/post/search/root"
        params = {"includeTags": [t.replace("_", " ") for t in self.tags]}
        return self._pagination(endpoint, params)
