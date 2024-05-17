# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hotleak.vip/"""

from .common import Extractor, Message
from .. import text, exception
import binascii

BASE_PATTERN = r"(?:https?://)?(?:www\.)?hotleak\.vip"


class HotleakExtractor(Extractor):
    """Base class for hotleak extractors"""
    category = "hotleak"
    directory_fmt = ("{category}", "{creator}",)
    filename_fmt = "{creator}_{id}.{extension}"
    archive_fmt = "{type}_{creator}_{id}"
    root = "https://hotleak.vip"

    def items(self):
        for post in self.posts():
            post["_http_expected_status"] = (404,)
            yield Message.Directory, post
            yield Message.Url, post["url"], post

    def posts(self):
        """Return an iterable containing relevant posts"""
        return ()

    def _pagination(self, url, params):
        params = text.parse_query(params)
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text
            if "</article>" not in page:
                return

            for item in text.extract_iter(
                    page, '<article class="movie-item', '</article>'):
                yield text.extr(item, '<a href="', '"')

            params["page"] += 1


def decode_video_url(url):
    # cut first and last 16 characters, reverse, base64 decode
    return binascii.a2b_base64(url[-17:15:-1]).decode()


class HotleakPostExtractor(HotleakExtractor):
    """Extractor for individual posts on hotleak"""
    subcategory = "post"
    pattern = (BASE_PATTERN + r"/(?!(?:hot|creators|videos|photos)(?:$|/))"
               r"([^/]+)/(photo|video)/(\d+)")
    example = "https://hotleak.vip/MODEL/photo/12345"

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self.creator, self.type, self.id = match.groups()

    def posts(self):
        url = "{}/{}/{}/{}".format(
            self.root, self.creator, self.type, self.id)
        page = self.request(url).text
        page = text.extr(
            page, '<div class="movie-image thumb">', '</article>')
        data = {
            "id"     : text.parse_int(self.id),
            "creator": self.creator,
            "type"   : self.type,
        }

        if self.type == "photo":
            data["url"] = text.extr(page, 'data-src="', '"')
            text.nameext_from_url(data["url"], data)

        elif self.type == "video":
            data["url"] = "ytdl:" + decode_video_url(text.extr(
                text.unescape(page), '"src":"', '"'))
            text.nameext_from_url(data["url"], data)
            data["extension"] = "mp4"

        return (data,)


class HotleakCreatorExtractor(HotleakExtractor):
    """Extractor for all posts from a hotleak creator"""
    subcategory = "creator"
    pattern = (BASE_PATTERN + r"/(?!(?:hot|creators|videos|photos)(?:$|/))"
               r"([^/?#]+)/?$")
    example = "https://hotleak.vip/MODEL"

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self.creator = match.group(1)

    def posts(self):
        url = "{}/{}".format(self.root, self.creator)
        return self._pagination(url)

    def _pagination(self, url):
        headers = {"X-Requested-With": "XMLHttpRequest"}
        params = {"page": 1}

        while True:
            try:
                response = self.request(
                    url, headers=headers, params=params, notfound="creator")
            except exception.HttpError as exc:
                if exc.response.status_code == 429:
                    self.wait(
                        until=exc.response.headers.get("X-RateLimit-Reset"))
                    continue
                raise

            posts = response.json()
            if not posts:
                return

            data = {"creator": self.creator}
            for post in posts:
                data["id"] = text.parse_int(post["id"])

                if post["type"] == 0:
                    data["type"] = "photo"
                    data["url"] = self.root + "/storage/" + post["image"]
                    text.nameext_from_url(data["url"], data)

                elif post["type"] == 1:
                    data["type"] = "video"
                    data["url"] = "ytdl:" + decode_video_url(
                        post["stream_url_play"])
                    text.nameext_from_url(data["url"], data)
                    data["extension"] = "mp4"

                yield data
            params["page"] += 1


class HotleakCategoryExtractor(HotleakExtractor):
    """Extractor for hotleak categories"""
    subcategory = "category"
    pattern = BASE_PATTERN + r"/(hot|creators|videos|photos)(?:/?\?([^#]+))?"
    example = "https://hotleak.vip/photos"

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self._category, self.params = match.groups()

    def items(self):
        url = "{}/{}".format(self.root, self._category)

        if self._category in ("hot", "creators"):
            data = {"_extractor": HotleakCreatorExtractor}
        elif self._category in ("videos", "photos"):
            data = {"_extractor": HotleakPostExtractor}

        for item in self._pagination(url, self.params):
            yield Message.Queue, item, data


class HotleakSearchExtractor(HotleakExtractor):
    """Extractor for hotleak search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search(?:/?\?([^#]+))"
    example = "https://hotleak.vip/search?search=QUERY"

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self.params = match.group(1)

    def items(self):
        data = {"_extractor": HotleakCreatorExtractor}
        for creator in self._pagination(self.root + "/search", self.params):
            yield Message.Queue, creator, data
