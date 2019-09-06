# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.lineblog.me/"""

from .livedoor import LivedoorBlogExtractor, LivedoorPostExtractor
from .. import text


class LineblogBase():
    """Base class for lineblog extractors"""
    category = "lineblog"
    root = "https://lineblog.me"

    def _images(self, post):
        imgs = []
        body = post.pop("body")

        for num, img in enumerate(text.extract_iter(body, "<img ", ">"), 1):
            src = text.extract(img, 'src="', '"')[0]
            alt = text.extract(img, 'alt="', '"')[0]

            if not src:
                continue
            if src.startswith("https://obs.line-scdn.") and src.count("/") > 3:
                src = src.rpartition("/")[0]

            imgs.append(text.nameext_from_url(alt or src, {
                "url" : src,
                "num" : num,
                "hash": src.rpartition("/")[2],
                "post": post,
            }))

        return imgs


class LineblogBlogExtractor(LineblogBase, LivedoorBlogExtractor):
    """Extractor for a user's blog on lineblog.me"""
    pattern = r"(?:https?://)?lineblog\.me/(\w+)/?(?:$|[?&#])"
    test = ("https://lineblog.me/mamoru_miyano/", {
        "range": "1-20",
        "count": 20,
        "pattern": r"https://obs.line-scdn.net/[\w-]+$",
        "keyword": {
            "post": {
                "categories" : tuple,
                "date"       : "type:datetime",
                "description": str,
                "id"         : int,
                "tags"       : list,
                "title"      : str,
                "user"       : "mamoru_miyano"
            },
            "filename": str,
            "hash"    : r"re:\w{32,}",
            "num"     : int,
        },
    })


class LineblogPostExtractor(LineblogBase, LivedoorPostExtractor):
    """Extractor for blog posts on lineblog.me"""
    pattern = r"(?:https?://)?lineblog\.me/(\w+)/archives/(\d+)"
    test = ("https://lineblog.me/mamoru_miyano/archives/1919150.html", {
        "url": "24afeb4044c554f80c374b52bf8109c6f1c0c757",
        "keyword": "76a38e2c0074926bd3362f66f9fc0e6c41591dcb",
    })
