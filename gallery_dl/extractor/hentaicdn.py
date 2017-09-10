# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors from sites based on hentaicdn"""

from .common import Extractor, Message
from .. import text
import json


class HentaicdnChapterExtractor(Extractor):
    """Base class for extractors for a single manga chapter"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga_id} {title}"]
    filename_fmt = ("{category}_{manga_id}_{chapter:>02}_"
                    "{num:>03}.{extension}")
    url = ""

    def items(self):
        page = self.request(self.url).text
        images = self.get_image_urls(page)
        data = self.get_job_metadata(page, images)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], part in enumerate(images, 1):
            url = "https://hentaicdn.com/hentai" + part
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page, images):
        """Collect metadata for extractor-job"""

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "var rff_imageList = ", ";")[0]
        return json.loads(images)
