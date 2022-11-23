# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hotleak.vip/"""

from .common import Extractor, Message
from .. import text, exception


class HotleakExtractor(Extractor):
    """Base class for hotleak extractors"""
    category = "hotleak"
    directory_fmt = ("{category}", "{creator}")
    filename_fmt = "{creator}_{id}.{extension}"
    archive_fmt = "{type}_{creator}_{id}"
    root = "https://hotleak.vip"
    cookiedomain = ".hotleak.vip"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root
        self.session.headers["User-Agent"] = self.config("user-agent") or \
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
             "rv:106.0) Gecko/20100101 Firefox/106.0")

    def items(self):
        for post in self.posts():
            yield Message.Directory, post
            yield Message.Url, post["url"], post

    def posts(self):
        """Return an iterable containing relevant posts"""
        return ()

    def _pagination(self, url):
        params = text.parse_query(self.params)
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text
            if "</article>" not in page:
                return
            for item in text.extract_iter(
                    page, '<article class="movie-item', '</article>'):
                yield text.extr(item, '<a href="', '"')
            params["page"] += 1


class HotleakPostExtractor(HotleakExtractor):
    """Extractor for individual posts on hotleak"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?hotleak\.vip"
               r"/(?!hot|creators|videos|photos)"
               r"([^/]+)/(photo|video)/(\d+)")
    test = (
        ("https://hotleak.vip/kaiyakawaii/photo/1617145", {
            "pattern": r"https://hotleak\.vip/storage/images/3625"
                       r"/1617145/fefdd5988dfcf6b98cc9e11616018868\.jpg",
            "keyword": {
                "id": 1617145,
                "creator": "kaiyakawaii",
                "type": "photo",
                "filename": "fefdd5988dfcf6b98cc9e11616018868",
                "extension": "jpg",
            },
        }),
        ("https://hotleak.vip/lilmochidoll/video/1625538", {
            "pattern": r"ytdl:https://cdn15-leak\.camhdxx\.com"
                       r"/[^/]+/1661/1625538/index\.m3u8",
            "keyword": {
                "id": 1625538,
                "creator": "lilmochidoll",
                "type": "video",
                "filename": "index",
                "extension": "mp4",
            },
        }),
    )

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self.creator, self.type, self.id = match.groups()

    def posts(self):
        url = "{}/{}/{}/{}".format(
            self.root, self.creator, self.type, self.id)
        page = text.extr(
            self.request(url).text, 'class="movie-image thumb">', '</article>')
        data = {
            "id"     : text.parse_int(self.id),
            "creator": self.creator,
            "type"   : self.type,
        }
        if self.type == "photo":
            data["url"] = text.extr(page, 'data-src="', '"')
            text.nameext_from_url(data["url"], data)

        elif self.type == "video":
            data["url"] = "ytdl:" + text.extr(
                text.unescape(page), '"src":"', '"')
            text.nameext_from_url(data["url"], data)
            data["extension"] = "mp4"
        return (data,)


class HotleakCreatorExtractor(HotleakExtractor):
    """Extractor for all posts from a hotleak creator"""
    subcategory = "creator"
    pattern = (r"(?:https?://)?(?:www\.)?hotleak\.vip"
               r"/(?!hot|creators|videos|photos)([^/?#]+)/?$")
    test = (
        ("https://hotleak.vip/kaiyakawaii", {
            "range": "1-50",
            "count": 50,
        }),
        ("https://hotleak.vip/stellaviolet", {
            "range": "1-50",
            "count": 50,
        }),
        ("https://hotleak.vip/doesnotexist", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self.creator = match.group(1)

    def posts(self):
        url = "{}/{}".format(self.root, self.creator)
        return self._pagination(url)

    def _pagination(self, url):
        self.session.headers["X-Requested-With"] = "XMLHttpRequest"
        params = {"page": 1}

        while True:
            response = self.request(url, params=params, notfound="creator")
            if response.status_code == 429:
                self.wait(
                    until=response.headers.get("X-RateLimit-Reset"))
                continue

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
                    data["url"] = "ytdl:" + post["stream_url_play"]
                    text.nameext_from_url(data["url"], data)
                    data["extension"] = "mp4"
                yield data
            params["page"] += 1


class HotleakCategoryExtractor(HotleakExtractor):
    """Extractor for hotleak categories"""
    subcategory = "category"
    pattern = (r"(?:https?://)?(?:www\.)?hotleak\.vip"
               r"/(hot|creators|videos|photos)(?:/?\?([^#]+))?")
    test = (
        ("https://hotleak.vip/photos", {
            "pattern": HotleakPostExtractor.pattern,
            "range": "1-10",
            "count": 10,
        }),
        ("https://hotleak.vip/videos"),
        ("https://hotleak.vip/creators", {
            "pattern": HotleakCreatorExtractor.pattern,
            "range": "1-10",
            "count": 10,
        }),
        ("https://hotleak.vip/hot"),
    )

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self._category, self.params = match.groups()

    def items(self):
        url = "{}/{}".format(self.root, self._category)

        if self._category in ("hot", "creators"):
            data = {"_extractor": HotleakCreatorExtractor}
        elif self._category in ("videos", "photos"):
            data = {"_extractor": HotleakPostExtractor}

        for item in self._pagination(url):
            yield Message.Queue, item, data


class HotleakSearchExtractor(HotleakExtractor):
    """Extractor for hotleak search results"""
    subcategory = "search"
    pattern = r"(?:https?://)?(?:www\.)?hotleak\.vip/search(?:/?\?([^#]+))"
    test = (
        ("https://hotleak.vip/search?search=gallery-dl", {
            "count": 0,
        }),
        ("https://hotleak.vip/search?search=hannah", {
            "count": "> 30",
        }),
    )

    def __init__(self, match):
        HotleakExtractor.__init__(self, match)
        self.params = match.group(1)

    def items(self):
        data = {"_extractor": HotleakCreatorExtractor}
        for creator in self._pagination(self.root + "/search"):
            yield Message.Queue, creator, data
