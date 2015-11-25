# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from https://www.mangamint.com/"""

from .common import Extractor, Message
from .. import text

class MangaMintExtractor(Extractor):

    category = "mangamint"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?mangamint\.com/([^\?]+-(\d+))"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.chapter = match.group(2)

    def items(self):
        page = self.request(self.url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(imgs, 1):
            data["page"] = num
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "category": self.category,
            "chapter": self.chapter,
            # "title": "",
            "lang": "en",
            "language": "English",
        }
        return text.extract_all(page, (
            (None, '<div class="left-corner2">', ''),
            (None, '<a href=">', ''),
            ('manga', '">', '<'),
        ), values=data)[0]


    def get_image_urls(self, page):
        """Extract list of all image-urls for a manga chapter"""
        params = {
            "manga_page": 0,
            "form_id": "select_similar_node_widget",
        }
        params["select_node"]  , pos = text.extract(page, r'"identifier":"node\/', '"')
        _                      , pos = text.extract(page, '>All pages<', '', pos)
        params["howmany"]      , pos = text.extract(page, 'value="', '"', pos-25)
        _                      , pos = text.extract(page, 'name="form_build_id"', '', pos)
        params["form_build_id"], pos = text.extract(page, 'value="', '"', pos)
        url = "http://www.mangamint.com/many/callback"
        page = self.request(url, method="post", data=params).json()["data"]
        imgs = []
        pos = 0
        while True:
            url, pos = text.extract(page, r'<img src ="', r'"', pos)
            if not url:
                return imgs
            imgs.append(url)
