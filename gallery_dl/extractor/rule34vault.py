# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34vault.com/"""

from .booru import BooruExtractor
from .. import text


class Rule34vaultExtractor(BooruExtractor):
    category = "rule34vault"
    root = "https://rule34vault.com"
    cdn_root = "https://r34xyz.b-cdn.net"
    filename_fmt = "{category}_{id}.{extension}"
    per_page = 100

    def _get_file_url(self, post_id, filetype):
        extension = "jpg" if filetype == "image" else "mp4"
        return "{}/posts/{}/{}/{}.{}".format(self.cdn_root,
                                             post_id // 1000,
                                             post_id,
                                             post_id,
                                             extension)

    def _parse_post(self, post_id):
        url = "{}/api/v2/post/{}".format(self.root, post_id)
        data = self.request(url).json()

        tags = " ".join(t["value"].replace(" ", "_") for t in data["tags"])
        post = {
            "id": post_id,
            "tags": tags,
            "uploader": data["uploader"]["userName"],
            "score": data.get("likes") or 0,
            "width": data["width"],
            "height": data["height"],
        }
        post["file_url"] = self._get_file_url(post_id,
                                              "image" if data['type'] == 0
                                              else "video")

        return post


class Rule34vaultPostExtractor(Rule34vaultExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?rule34vault\.com/post/(\d+)"
    example = "https://rule34vault.com/post/399437"

    def __init__(self, match):
        Rule34vaultExtractor.__init__(self, match)
        self.post_id = int(match.group(1))

    def posts(self):
        return (self._parse_post(self.post_id),)


class Rule34vaultPlaylistExtractor(Rule34vaultExtractor):
    subcategory = "playlist"
    directory_fmt = ("{category}", "{playlist_id}")
    archive_fmt = "t_{playlist_id}_{id}"
    pattern = r"(?:https?://)?rule34vault\.com/playlists/view/(\d+)"
    example = "https://rule34vault.com/playlists/view/2"

    def __init__(self, match):
        Rule34vaultExtractor.__init__(self, match)
        self.playlist_id = match.group(1)

    def metadata(self):
        return {"playlist_id": self.playlist_id}

    def posts(self):
        url = "{}/api/v2/post/search/playlist/{}".format(self.root,
                                                         self.playlist_id)
        current_page = self.page_start

        while True:
            payload = {
                "CountTotal": True,
                "Skip": current_page * self.per_page,
                "take": self.per_page,
            }
            data = self.request(url, method="POST", json=payload).json()

            for post in data["items"]:
                yield self._parse_post(post["id"])

            if current_page * self.per_page > data["totalCount"]:
                return
            current_page += 1


class Rule34vaultTagExtractor(Rule34vaultExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = r"(?:https?://)?rule34vault\.com/([^/?#]+)$"
    example = "https://rule34vault.com/not_porn"

    def __init__(self, match):
        Rule34vaultExtractor.__init__(self, match)
        self.tags_ = text.unquote(match.group(1)).split("%7C")
        self.tags = [t.replace("_", " ") for t in self.tags_]

    def metadata(self):
        return {"search_tags": " ".join(self.tags_)}

    def posts(self):
        url = '{}/api/v2/post/search/root'.format(self.root)
        current_page = self.page_start

        while True:
            payload = {
                "CountTotal": True,
                "Skip": current_page * self.per_page,
                "take": self.per_page,
                "includeTags": self.tags,
            }
            data = self.request(url, method="POST", json=payload).json()

            for post in data["items"]:
                yield self._parse_post(post["id"])

            if current_page * self.per_page > data['totalCount']:
                return
            current_page += 1
