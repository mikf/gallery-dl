# -*- coding: utf-8 -*-

# Copyright 2014-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://gelbooru.com/"""

from .common import Extractor, Message
from . import gelbooru_v02
from .. import text, exception
import binascii


class GelbooruBase():
    """Base class for gelbooru extractors"""
    category = "gelbooru"
    basecategory = "booru"
    root = "https://gelbooru.com"

    def _api_request(self, params):
        params["api_key"] = self.api_key
        params["user_id"] = self.user_id

        url = self.root + "/index.php?page=dapi&s=post&q=index&json=1"
        data = self.request(url, params=params).json()

        if "post" not in data:
            return ()

        posts = data["post"]
        if not isinstance(posts, list):
            return (posts,)
        return posts

    def _pagination(self, params):
        params["pid"] = self.page_start
        params["limit"] = self.per_page
        limit = self.per_page // 2

        while True:
            posts = self._api_request(params)

            for post in posts:
                yield post

            if len(posts) < limit:
                return

            if "pid" in params:
                del params["pid"]
            params["tags"] = "{} id:<{}".format(self.tags, post["id"])

    @staticmethod
    def _file_url(post):
        url = post["file_url"]
        if url.endswith((".webm", ".mp4")):
            md5 = post["md5"]
            path = "/images/{}/{}/{}.webm".format(md5[0:2], md5[2:4], md5)
            post["_fallback"] = GelbooruBase._video_fallback(path)
            url = "https://img3.gelbooru.com" + path
        return url

    @staticmethod
    def _video_fallback(path):
        yield "https://img2.gelbooru.com" + path
        yield "https://img1.gelbooru.com" + path


class GelbooruTagExtractor(GelbooruBase,
                           gelbooru_v02.GelbooruV02TagExtractor):
    """Extractor for images from gelbooru.com based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=list&tags=(?P<tags>[^&#]+)")
    test = (
        ("https://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
            "count": 5,
        }),
        ("https://gelbooru.com/index.php?page=post&s=list&tags=meiya_neon", {
            "range": "196-204",
            "url": "845a61aa1f90fb4ced841e8b7e62098be2e967bf",
            "pattern": r"https://img\d\.gelbooru\.com"
                       r"/images/../../[0-9a-f]{32}\.jpg",
            "count": 9,
        }),
    )


class GelbooruPoolExtractor(GelbooruBase,
                            gelbooru_v02.GelbooruV02PoolExtractor):
    """Extractor for gelbooru pools"""
    per_page = 45
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=pool&s=show&id=(?P<pool>\d+)")
    test = (
        ("https://gelbooru.com/index.php?page=pool&s=show&id=761", {
            "count": 6,
        }),
    )

    def metadata(self):
        url = self.root + "/index.php"
        self._params = {
            "page": "pool",
            "s"   : "show",
            "id"  : self.pool_id,
            "pid" : self.page_start,
        }
        self._page = self.request(url, params=self._params).text

        name, pos = text.extract(self._page, "<h3>Now Viewing: ", "</h3>")
        if not name:
            raise exception.NotFoundError("pool")

        return {
            "pool": text.parse_int(self.pool_id),
            "pool_name": text.unescape(name),
        }

    def posts(self):
        url = self.root + "/index.php"
        params = self._params

        page = self._page
        del self._page
        data = {}

        while True:
            num_ids = 0
            for data["id"] in text.extract_iter(page, '" id="p', '"'):
                num_ids += 1
                yield from self._api_request(data)

            if num_ids < self.per_page:
                return
            params["pid"] += self.per_page
            page = self.request(url, params=params).text


class GelbooruPostExtractor(GelbooruBase,
                            gelbooru_v02.GelbooruV02PostExtractor):
    """Extractor for single images from gelbooru.com"""
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=view&id=(?P<post>\d+)")
    test = (
        ("https://gelbooru.com/index.php?page=post&s=view&id=313638", {
            "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
            "count": 1,
        }),
        ("https://gelbooru.com/index.php?page=post&s=view&id=6018318", {
            "options": (("tags", True),),
            "content": "977caf22f27c72a5d07ea4d4d9719acdab810991",
            "keyword": {
                "tags_artist": "kirisaki_shuusei",
                "tags_character": str,
                "tags_copyright": "vocaloid",
                "tags_general": str,
                "tags_metadata": str,
            },
        }),
        # video
        ("https://gelbooru.com/index.php?page=post&s=view&id=5938076", {
            "content": "6360452fa8c2f0c1137749e81471238564df832a",
            "pattern": r"https://img\d\.gelbooru\.com/images"
                       r"/22/61/226111273615049235b001b381707bd0\.webm",
        }),
        # notes
        ("https://gelbooru.com/index.php?page=post&s=view&id=5997331", {
            "options": (("notes", True),),
            "keywords": {
                "notes": [
                    {
                        "height": 553,
                        "body": "Look over this way when you talk~",
                        "width": 246,
                        "x": 35,
                        "y": 72
                    },
                    {
                        "height": 557,
                        "body": "Hey~\nAre you listening~?",
                        "width": 246,
                        "x": 1233,
                        "y": 109
                    }
                ]
            }
        }),
    )


class GelbooruRedirectExtractor(GelbooruBase, Extractor):
    subcategory = "redirect"
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com"
               r"/redirect\.php\?s=([^&#]+)")
    test = (("https://gelbooru.com/redirect.php?s=Ly9nZWxib29ydS5jb20vaW5kZXgu"
             "cGhwP3BhZ2U9cG9zdCZzPXZpZXcmaWQ9MTgzMDA0Ng=="), {
        "pattern": r"https://gelbooru.com/index.php"
                   r"\?page=post&s=view&id=1830046"
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.redirect_url = text.ensure_http_scheme(
            binascii.a2b_base64(match.group(1)).decode())

    def items(self):
        data = {"_extractor": GelbooruPostExtractor}
        yield Message.Queue, self.redirect_url, data
