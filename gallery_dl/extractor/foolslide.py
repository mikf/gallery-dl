# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for FoOlSlide based sites"""

from .common import BaseExtractor, Message
from .. import text, util


class FoolslideExtractor(BaseExtractor):
    """Base class for FoOlSlide extractors"""
    basecategory = "foolslide"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.gallery_url = self.root + match.group(match.lastindex)

    def request(self, url):
        return BaseExtractor.request(
            self, url, encoding="utf-8", method="POST", data={"adult": "true"})

    @staticmethod
    def parse_chapter_url(url, data):
        info = url.partition("/read/")[2].rstrip("/").split("/")
        lang = info[1].partition("-")[0]
        data["lang"] = lang
        data["language"] = util.code_to_language(lang)
        data["volume"] = text.parse_int(info[2])
        data["chapter"] = text.parse_int(info[3])
        data["chapter_minor"] = "." + info[4] if len(info) >= 5 else ""
        data["title"] = data["chapter_string"].partition(":")[2].strip()
        return data


BASE_PATTERN = FoolslideExtractor.update({
})


class FoolslideChapterExtractor(FoolslideExtractor):
    """Base class for chapter extractors for FoOlSlide based sites"""
    subcategory = "chapter"
    directory_fmt = ("{category}", "{manga}", "{chapter_string}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor:?//}_{page:>03}.{extension}")
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"(/read/[^/?#]+/[a-z-]+/\d+/\d+(?:/\d+)?)"
    example = "https://read.powermanga.org/read/MANGA/en/0/123/"

    def items(self):
        page = self.request(self.gallery_url).text
        data = self.metadata(page)
        imgs = self.images(page)

        data["count"] = len(imgs)
        data["chapter_id"] = text.parse_int(imgs[0]["chapter_id"])

        yield Message.Directory, data
        enum = util.enumerate_reversed if self.config(
            "page-reverse") else enumerate
        for data["page"], image in enum(imgs, 1):
            try:
                url = image["url"]
                del image["url"]
                del image["chapter_id"]
                del image["thumb_url"]
            except KeyError:
                pass
            for key in ("height", "id", "size", "width"):
                image[key] = text.parse_int(image[key])
            data.update(image)
            text.nameext_from_url(data["filename"], data)
            yield Message.Url, url, data

    def metadata(self, page):
        extr = text.extract_from(page)
        extr('<h1 class="tbtitle dnone">', '')
        return self.parse_chapter_url(self.gallery_url, {
            "manga"         : text.unescape(extr('title="', '"')).strip(),
            "chapter_string": text.unescape(extr('title="', '"')),
        })

    def images(self, page):
        return util.json_loads(text.extr(page, "var pages = ", ";"))


class FoolslideMangaExtractor(FoolslideExtractor):
    """Base class for manga extractors for FoOlSlide based sites"""
    subcategory = "manga"
    categorytransfer = True
    pattern = BASE_PATTERN + r"(/series/[^/?#]+)"
    example = "https://read.powermanga.org/series/MANGA/"

    def items(self):
        page = self.request(self.gallery_url).text

        chapters = self.chapters(page)
        if not self.config("chapter-reverse", False):
            chapters.reverse()

        for chapter, data in chapters:
            data["_extractor"] = FoolslideChapterExtractor
            yield Message.Queue, chapter, data

    def chapters(self, page):
        extr = text.extract_from(page)
        manga = text.unescape(extr('<h1 class="title">', '</h1>')).strip()
        author = extr('<b>Author</b>: ', '<br')
        artist = extr('<b>Artist</b>: ', '<br')

        results = []
        while True:
            url = extr('<div class="title"><a href="', '"')
            if not url:
                return results
            results.append((url, self.parse_chapter_url(url, {
                "manga": manga, "author": author, "artist": artist,
                "chapter_string": extr('title="', '"'),
                "group"         : extr('title="', '"'),
            })))
