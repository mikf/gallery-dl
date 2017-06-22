# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for FoOlSlide based sites"""

from .common import Extractor, MangaExtractor, Message
from .. import text, util
import json


CHAPTER_RE = (
    r"/read/[^/]+"
    r"/(?P<lang>[a-z]{2})"
    r"/(?P<volume>\d+)"
    r"/(?P<chapter>\d+)"
    r"(?:/(?P<chapter_minor>\d+))?)"
)

MANGA_RE = (
    r"/series/[^/]+/?$)"
)


def chapter_pattern(domain_re):
    return [r"(?:https?://)?(" + domain_re + CHAPTER_RE]


def manga_pattern(domain_re):
    return [r"(?:https?://)?(" + domain_re + MANGA_RE]


class FoolslideChapterExtractor(Extractor):
    """Base class for chapter extractors for FoOlSlide based sites"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{chapter_string}"]
    filename_fmt = "{manga}_{chapter:>03}_{page:>03}.{extension}"
    scheme = "https"
    single = True

    def __init__(self, match, url=None):
        Extractor.__init__(self)
        self.url = url or self.scheme + "://" + match.group(1)
        self.data = match.groupdict(default="")

    def items(self):
        page = self.request(self.url, encoding="utf-8",
                            method="post", data={"adult": "true"}).text
        data = self.get_metadata(page)
        imgs = self.get_images(page)

        data["count"] = len(imgs)
        data["chapter_id"] = imgs[0]["chapter_id"]

        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], image in enumerate(imgs, 1):
            try:
                url = image["url"]
                del image["url"]
                del image["thumb_url"]
            except KeyError:
                pass
            data.update(image)
            text.nameext_from_url(data["filename"], data)
            yield Message.Url, url, data

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        _      , pos = text.extract(page, '<h1 class="tbtitle dnone">', '')
        manga  , pos = text.extract(page, 'title="', '"', pos)
        chapter, pos = text.extract(page, 'title="', '"', pos)

        chapter = text.unescape(chapter)
        parts = chapter.split(":", maxsplit=1)
        title = parts[1].strip() if len(parts) > 1 else ""

        self.data["manga"] = text.unescape(manga).strip()
        self.data["title"] = title
        self.data["language"] = util.code_to_language(self.data["lang"])
        self.data["chapter_string"] = chapter
        return self.data

    def get_images(self, page):
        """Return a list of all images in this chapter"""
        if self.single:
            pos = 0
            needle = "var pages = "
        else:
            pos = page.find("[{")
            needle = " = "
        return json.loads(text.extract(page, needle, ";", pos)[0])


class FoolslideMangaExtractor(MangaExtractor):
    """Base class for manga extractors for FoOlSlide based sites"""
    scheme = "https"

    def request(self, url):
        return MangaExtractor.request(
            self, url, encoding="utf-8", method="post", data={"adult": "true"}
        )

    def chapters(self, page):
        """Return a list of all chapter urls"""
        return list(text.extract_iter(
            page, '<div class="title"><a href="', '"'
        ))
