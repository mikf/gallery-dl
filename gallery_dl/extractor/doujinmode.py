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

    category = "doujinmode"
    directory_fmt = ["{category}", "{title}"]
    filename_fmt = "{num:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?doujinmode\.net/(?:hentai/)?mangas/([0-9a-f]{36})"]
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
            "category": self.category,
            "gallery-id": self.gid,
            "title": title,
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
