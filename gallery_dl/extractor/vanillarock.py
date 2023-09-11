# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
    example = "https://vanilla-rock.com/TITLE"

    def items(self):
        extr = text.extract_from(self.request(self.root + self.path).text)
        name = extr('<h1 class="entry-title">', "<")

        imgs = []
        while True:
            img = extr('<div class="main-img">', '</div>')
            if not img:
                break
            imgs.append(text.extr(img, 'href="', '"'))

        data = {
            "count": len(imgs),
            "title": text.unescape(name),
            "path" : self.path.strip("/"),
            "date" : text.parse_datetime(extr(
                '<div class="date">', '</div>'), "%Y-%m-%d %H:%M"),
            "tags" : text.split_html(extr(
                '<div class="cat-tag">', '</div>'))[::2],
        }

        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)


class VanillarockTagExtractor(VanillarockExtractor):
    """Extractor for vanillarock blog posts by tag or category"""
    subcategory = "tag"
    pattern = (r"(?:https?://)?(?:www\.)?vanilla-rock\.com"
               r"(/(?:tag|category)/[^?#]+)")
    example = "https://vanilla-rock.com/tag/TAG"

    def items(self):
        url = self.root + self.path
        data = {"_extractor": VanillarockPostExtractor}

        while url:
            extr = text.extract_from(self.request(url).text)
            while True:
                post = extr('<h2 class="entry-title">', '</h2>')
                if not post:
                    break
                yield Message.Queue, text.extr(post, 'href="', '"'), data
            url = text.unescape(extr('class="next page-numbers" href="', '"'))
