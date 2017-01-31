# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for FoolSlide based sites"""

from .common import Extractor, Message
from .. import text, iso639_1
import json
import re


class FoolslideChapterExtractor(Extractor):
    """Base class for chapter extractors on foolslide based sites"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{chapter:>03} - {title}"]
    filename_fmt = "{manga}_{chapter:>03}_{page:>03}.{extension}"
    single = True

    def __init__(self, url, lang):
        Extractor.__init__(self)
        self.url = url
        self.lang = lang

    def items(self):
        page = self.request(self.url, encoding="utf-8",
                            method="post", data={"adult": "true"}).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], image in enumerate(self.get_images(page), 1):
            try:
                url = image["url"]
                del image["url"]
                del image["thumb_url"]
            except KeyError:
                pass
            data.update(image)
            text.nameext_from_url(data["filename"], data)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        _        , pos = text.extract(page, '<h1 class="tbtitle dnone">', '')
        manga    , pos = text.extract(page, 'title="', '"', pos)
        chapter  , pos = text.extract(page, '">', '</a>', pos)

        parts = chapter.split(":", maxsplit=1)
        match = re.match(r"(?:Vol.(\d+) )?(?:Chapter (\d+)$|(.+))", parts[0])
        volume = match.group(1) or ""
        chapter = match.group(2) or match.group(3).strip()

        return {
            "manga": text.unescape(manga),
            "chapter": chapter,
            "volume": volume,
            "lang": self.lang,
            "language": iso639_1.code_to_language(self.lang),
            "title": text.unescape(parts[1].strip() if len(parts) > 1 else ""),
        }

    def get_images(self, page):
        """Return a list of all images in this chapter"""
        if self.single:
            pos = 0
            needle = "var pages = "
        else:
            pos = page.find("[{")
            needle = " = "
        return json.loads(text.extract(page, needle, ";", pos)[0])
