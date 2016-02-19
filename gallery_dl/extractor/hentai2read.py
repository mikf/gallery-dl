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

class Hentai2ReadExtractor(Extractor):

    category = "hentai2read"
    directory_fmt = ["{category}", "{gallery-id}"]
    filename_fmt = "{category}_{gallery-id}_{num:>03}_{name}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/(\d+)"]
    test = [("http://hentai2read.com/amazon_elixir/1/", {
        "url": "fb5fc4d7cc194116960eaa648c7e045a6e6f0c11",
        "keyword": "4ab36b0cc426747c347fe563caba601455222a78",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url_title, self.chapter = match.groups()

    def items(self):
        page = self.request("http://hentai2read.com/" + self.url_title + "/1").text
        images = self.get_image_urls(page)
        data = self.get_job_metadata(page, images)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(images, 1):
            data["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page, images):
        """Collect metadata for extractor-job"""
        return {
            "category": self.category,
            "gallery-id": images[0].split("/")[-3],
            "chapter": self.chapter,
            "count": len(images),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "var wpm_mng_rdr_img_lst = ", ";")[0]
        return json.loads(images)
