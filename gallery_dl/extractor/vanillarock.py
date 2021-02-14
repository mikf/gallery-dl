# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vanilla-rock.com/"""

from .common import Extractor, Message
from .. import text


class VanillarockExtractor(Extractor):
    """Base class for vanillarock extractors"""
    category = "vanillarock"
    root = "https://vanilla-rock.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)


class VanillarockPostExtractor(VanillarockExtractor):
    """Extractor for blogposts on vanilla-rock.com"""
    subcategory = "post"
    directory_fmt = ("{category}", "{path}")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{filename}"
    pattern = (r"(?:https?://)?(?:www\.)?vanilla-rock\.com"
               r"(/(?!category/|tag/)[^/?#]+)/?$")
    test = ("https://vanilla-rock.com/mizuhashi_parsee-5", {
        "url": "7fb9a4d18d9fa22d7295fee8d94ab5a7a52265dd",
        "keyword": "b91df99b714e1958d9636748b1c81a07c3ef52c9",
    })

    def items(self):
        extr = text.extract_from(self.request(self.root + self.path).text)
        name = extr('<h1 class="entry-title">', "<")

        imgs = []
        while True:
            img = extr('<div class="main-img">', '</div>')
            if not img:
                break
            imgs.append(text.extract(img, 'href="', '"')[0])

        data = {
            "count": len(imgs),
            "title": text.unescape(name),
            "path" : self.path.strip("/"),
            "date" : text.parse_datetime(extr(
                '<div class="date">', '</div>'), "%Y-%m-%d %H:%M"),
            "tags" : text.split_html(extr(
                '<div class="cat-tag">', '</div>'))[::2],
        }

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)


class VanillarockTagExtractor(VanillarockExtractor):
    """Extractor for vanillarock blog posts by tag or category"""
    subcategory = "tag"
    pattern = (r"(?:https?://)?(?:www\.)?vanilla-rock\.com"
               r"(/(?:tag|category)/[^?#]+)")
    test = (
        ("https://vanilla-rock.com/tag/%e5%b0%84%e5%91%bd%e4%b8%b8%e6%96%87", {
            "pattern": VanillarockPostExtractor.pattern,
            "count": ">= 12",
        }),
        (("https://vanilla-rock.com/category/%e4%ba%8c%e6%ac%a1%e3%82%a8%e3%83"
          "%ad%e7%94%bb%e5%83%8f/%e8%90%8c%e3%81%88%e3%83%bb%e3%82%bd%e3%83%95"
          "%e3%83%88%e3%82%a8%e3%83%ad"), {
            "pattern": VanillarockPostExtractor.pattern,
            "count": ">= 5",
        }),
    )

    def items(self):
        url = self.root + self.path
        data = {"_extractor": VanillarockPostExtractor}

        yield Message.Version, 1
        while url:
            extr = text.extract_from(self.request(url).text)
            while True:
                post = extr('<h2 class="entry-title">', '</h2>')
                if not post:
                    break
                yield Message.Queue, text.extract(post, 'href="', '"')[0], data
            url = text.unescape(extr('class="next page-numbers" href="', '"'))
