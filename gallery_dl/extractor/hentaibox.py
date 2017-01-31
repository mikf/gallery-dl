# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.hentaibox.net/"""

from .common import Extractor, Message
from .. import text, iso639_1


class HentaiboxChapterExtractor(Extractor):
    """Extractor for a single manga chapter from hentaibox.net"""
    category = "hentaibox"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{series}", "{title}"]
    filename_fmt = "{num:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?hentaibox\.net/"
               r"[^/]+/(\d+)_\d+_([^/&]+)"]
    test = [(("http://www.hentaibox.net/hentai-manga/"
              "16_18_Original_Amazon-No-Hiyaku-Amazon-Elixir-Decensored"), {
        "url": "d1a50a9b289d284f178971e01cf312791888e057",
        "keyword": "b4b100f800b716e573e072f01b5d604d9b436b70",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.count = match.group(1)

    def items(self):
        page = self.request(self.url + "&slideshow=play").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(self.get_image_urls(page), 1):
            data["num"] = num
            data["extension"] = url[url.rfind(".")+1:]
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = text.extract_all(page, (
            ("title"   , 'content="Read or Download ', ' hentai manga from'),
            ("series"  , ' the series ', ' with ' + self.count),
            ("language", ' translated pages to ', '.'),
        ), values={"count": self.count})[0]
        data["lang"] = iso639_1.language_to_code(data["language"])
        return data

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        yield from text.extract_iter(
            page, '<span class="slideshow_path">', '</span>'
        )
