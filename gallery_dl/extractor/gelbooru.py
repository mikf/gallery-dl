# -*- coding: utf-8 -*-

# Copyright 2014-2021 Mike Fährmann
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

    @staticmethod
    def _file_url(post):
        url = post["file_url"]
        if url.startswith(("https://mp4.gelbooru.com/", "https://video-cdn")):
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
        ("https://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
            "options": (("api", False),),
            "count": 5,
        }),
    )


class GelbooruPoolExtractor(GelbooruBase,
                            gelbooru_v02.GelbooruV02PoolExtractor):
    """Extractor for image-pools from gelbooru.com"""
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=pool&s=show&id=(?P<pool>\d+)")
    test = (
        ("https://gelbooru.com/index.php?page=pool&s=show&id=761", {
            "count": 6,
        }),
        ("https://gelbooru.com/index.php?page=pool&s=show&id=761", {
            "options": (("api", False),),
            "count": 6,
        }),
    )

    def metadata(self):
        url = "{}/index.php?page=pool&s=show&id={}".format(
            self.root, self.pool_id)
        page = self.request(url).text

        name, pos = text.extract(page, "<h3>Now Viewing: ", "</h3>")
        if not name:
            raise exception.NotFoundError("pool")
        self.post_ids = text.extract_iter(page, 'class="" id="p', '"', pos)

        return {
            "pool": text.parse_int(self.pool_id),
            "pool_name": text.unescape(name),
        }


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
