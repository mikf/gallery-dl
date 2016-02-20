# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://hentai2read.com/"""

from .common import Extractor, Message
from .. import text
import json
import re

class Hentai2ReadChapterExtractor(Extractor):

    category = "hentai2read"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{chapter:>02}_{num:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/(\d+)"]
    test = [("http://hentai2read.com/amazon_elixir/1/", {
        "url": "fb5fc4d7cc194116960eaa648c7e045a6e6f0c11",
        "keyword": "03435037539d57ca084c457b5ac4d48928487521",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url_title, self.chapter = match.groups()

    def items(self):
        url = "http://hentai2read.com/{}/{}/".format(self.url_title, self.chapter)
        page = self.request(url).text
        images = self.get_image_urls(page)
        data = self.get_job_metadata(page, images)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(images, 1):
            data["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page, images):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<title>", "</title>")[0]
        match = re.match(r"Reading (?:(.+) dj - )?(.+) Hentai - \d+: ", title)
        return {
            "category": self.category,
            "gallery-id": images[0].split("/")[-3],
            "chapter": self.chapter,
            "count": len(images),
            "series": match.group(1) or "",
            "title": match.group(2),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "var wpm_mng_rdr_img_lst = ", ";")[0]
        return json.loads(images)
