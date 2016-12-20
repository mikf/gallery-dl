# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract comic issues from http://readcomics.tv/"""

from .common import Extractor, Message
from .. import text


class ReadcomicsIssueExtractor(Extractor):
    """Extractor for comic-issues from readcomics.tv"""
    category = "readcomics"
    subcategory = "issue"
    directory_fmt = ["{category}", "{comic}", "{issue:>03}"]
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?readcomics\.(?:tv|net)/"
                r"([^/]+)/chapter-(\d+)")]
    root = "https://readcomics.tv"

    def __init__(self, match):
        Extractor.__init__(self)
        self.comic, self.chapter = match.groups()

    def items(self):
        url = "{}/{}/chapter-{}/full".format(self.root, self.comic, self.chapter)
        page = self.request(url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        info = text.extract(page, "<title>", " - Read ")[0].rsplit(maxsplit=1)
        return {
            "comic": info[0],
            "issue": info[1][1:],
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract list of all image-urls for a comic-issue"""
        needle = ('class="chapter_img" style="margin-bottom: '
                  '20px; max-width: 100%;" src="')
        return list(text.extract_iter(page, needle, '"'))
