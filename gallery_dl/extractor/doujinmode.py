# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://doujinmode.net/"""

from .common import Extractor, Message
from .. import text
import re

class DoujinmodeChapterExtractor(Extractor):
    """Extractor for manga-/doujinshi-chapters from doujinmode.net"""
    category = "doujinmode"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{title}"]
    filename_fmt = "{num:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?doujinmode\.net/"
                r"(?:hentai/|yaoi/|western/)?mangas/([0-9a-f]{36})")]
    test = [("http://doujinmode.net/mangas/967836c988a716e9efca06998b7838d09eb5", {
        "url": "be5d48a9fd48f09cfcc5d4e51f24bf1100e75502",
        "keyword": "fbccd0416f19080dc2e041917aeff721399adf13",
        "content": "a041114e2a8af54d42a4a46a69cae4ebf2641cb1",
    })]
    url_base = "http://doujinmode.net/mangas/"

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images():
            data.update(image)
            yield Message.Url, url, data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request(self.url_base + self.gid).text
        count, pos = text.extract(page, ' class="manga-count">', '</span>')
        title, pos = text.extract(page, '<h2>', ' Images List</h2>', pos)
        return {
            "gallery-id": self.gid,
            "title": text.unescape(title),
            "count": count,
        }

    def get_images(self):
        """Collect a list of all images with url and metadata"""
        url = self.url_base + "pages_large?manga_uuid=" + self.gid
        for page in self.request(url).json():
            pattern = r"(.*/p/([^/]+)/).+(\.(\w+)\?(\d+))"
            parts = re.match(pattern, page["image_url"]).groups()
            yield parts[0] + "original" + parts[2], {
                "num": page["page"],
                "image-id": parts[1],
                "extension": parts[3],
                "timestamp": parts[4],
            }
