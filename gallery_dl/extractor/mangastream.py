# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://mangastream.com/"""

from .common import AsynchronousExtractor, Message
from .. import text
from urllib.parse import urljoin


class MangastreamChapterExtractor(AsynchronousExtractor):
    """Extractor for manga-chapters from mangastream.com"""
    category = "mangastream"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter} - {title}"]
    filename_fmt = "{manga}_c{chapter}_{page:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?(?:readms|mangastream)\.(?:com|net)/"
                r"r(?:ead)?/([^/]*/([^/]+)/(\d+))")]
    root = "https://readms.net/r/"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.part, self.chapter, self.ch_id = match.groups()

    def items(self):
        page = self.request(self.root + self.part).text
        data = self.get_job_metadata(page)
        next_url = None
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"] in range(1, int(data["count"])+1):
            if next_url:
                page = self.request(next_url).text
            next_url, image_url = self.get_page_metadata(page)
            text.nameext_from_url(image_url, data)
            image_url = urljoin(self.root, image_url)
            yield Message.Url, image_url, data.copy()

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        manga, pos = text.extract(
            page, '<span class="hidden-xs hidden-sm">', "<"
        )
        pos = page.find(self.part, pos)
        title, pos = text.extract(page, ' - ', '<', pos)
        count, pos = text.extract(page, 'Last Page (', ')', pos)
        data = {
            "manga": manga,
            "chapter": text.unquote(self.chapter),
            "chapter-id": self.ch_id,
            "title": title,
            "count": count,
            "lang": "en",
            "language": "English",
        }
        return data

    @staticmethod
    def get_page_metadata(page):
        """Collect next url, image-url and metadata for one manga-page"""
        nurl, pos = text.extract(page, '<div class="page">\n<a href="', '"')
        iurl, pos = text.extract(page, '<img id="manga-page" src="', '"', pos)
        return nurl, iurl
