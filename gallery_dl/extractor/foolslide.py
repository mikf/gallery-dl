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
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}"

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
        match = re.match(r"(\w+ (\d+)([^:+]*)(?:: (.*))?|[^:]+)", chapter)
        return {
            "manga": text.unescape(manga),
            "chapter": match.group(2) or match.group(1),
            "chapter-minor": match.group(3) or "",
            "lang": self.lang,
            "language": iso639_1.code_to_language(self.lang),
            "title": text.unescape(match.group(4) or ""),
        }

    @staticmethod
    def get_images(page):
        """Return a list of all images in this chapter"""
        return json.loads(text.extract(page, 'var pages = ', ';')[0])
