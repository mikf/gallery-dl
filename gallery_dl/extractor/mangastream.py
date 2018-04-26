# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://mangastream.com/"""

from .common import ChapterExtractor
from .. import text


class MangastreamChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from mangastream.com"""
    category = "mangastream"
    archive_fmt = "{chapter_id}_{page}"
    pattern = [(r"(?:https?://)?(?:www\.)?(?:readms|mangastream)\.(?:com|net)/"
                r"r(?:ead)?/([^/]*/([^/]+)/(\d+))")]
    test = [("https://readms.net/r/onepunch_man/087/4874/1", None)]
    base_url = "https://readms.net/r/"

    def __init__(self, match):
        self.part, self.chapter, self.ch_id = match.groups()
        ChapterExtractor.__init__(self, self.base_url + self.part)

    def get_metadata(self, page):
        manga, pos = text.extract(
            page, '<span class="hidden-xs hidden-sm">', "<")
        pos = page.find(self.part, pos)
        title, pos = text.extract(page, ' - ', '<', pos)
        count, pos = text.extract(page, 'Last Page (', ')', pos)
        return {
            "manga": manga,
            "chapter": text.unquote(self.chapter),
            "chapter_id": text.parse_int(self.ch_id),
            "title": title,
            "count": text.parse_int(count, 1),
            "lang": "en",
            "language": "English",
        }

    def get_images(self, page):
        while True:
            pos = page.index(' class="page"')
            next_url = text.extract(page, ' href="', '"', pos)[0]
            image_url = text.extract(page, ' src="', '"', pos)[0]
            yield text.urljoin(self.base_url, image_url), None
            page = self.request(text.urljoin(self.base_url, next_url)).text
