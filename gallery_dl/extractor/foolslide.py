# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for FoOlSlide based sites"""

from .common import SharedConfigExtractor, MangaExtractor, Message
from .. import text, util
import base64
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


class FoolslideExtractor(SharedConfigExtractor):
    """Base class for FoOlSlide extractors"""
    basecategory = "foolslide"
    scheme = "https"

    def request(self, url):
        return SharedConfigExtractor.request(
            self, url, encoding="utf-8", method="post", data={"adult": "true"})

    @staticmethod
    def parse_chapter_url(url, data):
        info = url.partition("/read/")[2].rstrip("/").split("/")
        data["lang"] = info[1]
        data["language"] = util.code_to_language(info[1])
        data["volume"] = util.safe_int(info[2])
        data["chapter"] = util.safe_int(info[3])
        data["chapter_minor"] = "." + info[4] if len(info) >= 5 else ""
        return data


class FoolslideChapterExtractor(FoolslideExtractor):
    """Base class for chapter extractors for FoOlSlide based sites"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{chapter_string}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    method = "default"

    def __init__(self, match, url=None):
        FoolslideExtractor.__init__(self)
        self.url = url or self.scheme + "://" + match.group(1)

    def items(self):
        page = self.request(self.url).text
        data = self.get_metadata(page)
        imgs = self.get_images(page)

        data["count"] = len(imgs)
        data["chapter_id"] = util.safe_int(imgs[0]["chapter_id"])

        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], image in enumerate(imgs, 1):
            try:
                url = image["url"]
                del image["url"]
                del image["chapter_id"]
                del image["thumb_url"]
            except KeyError:
                pass
            for key in ("height", "id", "size", "width"):
                image[key] = util.safe_int(image[key])
            data.update(image)
            text.nameext_from_url(data["filename"], data)
            yield Message.Url, url, data

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        _      , pos = text.extract(page, '<h1 class="tbtitle dnone">', '')
        manga  , pos = text.extract(page, 'title="', '"', pos)
        chapter, pos = text.extract(page, 'title="', '"', pos)
        chapter = text.unescape(chapter)
        return self.parse_chapter_url(self.url, {
            "manga": text.unescape(manga).strip(),
            "title": chapter.partition(":")[2].strip(),
            "chapter_string": chapter,
        })

    def get_images(self, page):
        """Return a list of all images in this chapter"""
        if self.method == "base64":
            base64_data = text.extract(page, 'atob("', '"')[0].encode()
            data = base64.b64decode(base64_data).decode()
        elif self.method == "double":
            pos = page.find("[{")
            data = text.extract(page, " = ", ";", pos)[0]
        else:
            data = text.extract(page, "var pages = ", ";")[0]
        return json.loads(data)


class FoolslideMangaExtractor(FoolslideExtractor, MangaExtractor):
    """Base class for manga extractors for FoOlSlide based sites"""

    def chapters(self, page):
        """Return a list of all chapter urls"""
        manga , pos = text.extract(page, '<h1 class="title">', '</h1>')
        author, pos = text.extract(page, '<b>Author</b>: ', '<br', pos)
        artist, pos = text.extract(page, '<b>Artist</b>: ', '<br', pos)
        manga = text.unescape(manga).strip()

        results = []
        while True:
            url, pos = text.extract(
                page, '<div class="title"><a href="', '"', pos)
            if not url:
                return results

            chapter, pos = text.extract(page, 'title="', '"', pos)
            group  , pos = text.extract(page, 'title="', '"', pos)

            results.append((url, self.parse_chapter_url(url, {
                "manga": manga, "author": author, "artist": artist,
                "group": group, "chapter_string": chapter,
                "title": chapter.partition(": ")[2] or "",
            })))
