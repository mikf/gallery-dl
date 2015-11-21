# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://bato.to/"""

from .common import AsynchronousExtractor, Message
from .. import text, iso639_1
import re

class BatotoExtractor(AsynchronousExtractor):

    category = "batoto"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?bato\.to/reader#([0-9a-f]+)"]
    url = "https://bato.to/areader"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.token = match.group(1)
        self.session.headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://bato.to/reader",
        })

    def items(self):
        params = {
            "id": self.token,
            "p": 1,
            "supress_webtoon": "t",
        }
        page = self.request(self.url, params=params).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        for i in range(int(data["count"])):
            next_url, image_url = self.get_page_urls(page)
            text.nameext_from_url(image_url, data)
            data["page"] = i+1
            yield Message.Url, image_url, data.copy()
            if next_url:
                params["p"] += 1
                page = self.request(self.url, params=params).text

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        extr = text.extract
        _    , pos = extr(page, '<select name="chapter_select"', '')
        cinfo, pos = extr(page, 'selected="selected">', '</option>', pos)
        _    , pos = extr(page, '<select name="group_select"', '', pos)
        group, pos = extr(page, 'selected="selected">', ' - ', pos)
        lang , pos = extr(page, '', '</option>', pos)
        _    , pos = extr(page, '<select name="page_select"', '', pos)
        _    , pos = extr(page, '</select>', '', pos)
        count, pos = extr(page, '>page ', '<', pos-35)
        manga, pos = extr(page, "document.title = '", " - ", pos)
        match = re.match(r"(Vol.(\d+) )?Ch.(\d+)([^:]*)(: (.+))?", cinfo)
        return {
            "category": self.category,
            "token": self.token,
            "manga": manga,
            "volume": match.group(2) or "",
            "chapter": match.group(3),
            "chapter-extra": match.group(4),
            "title": match.group(6) or "",
            "group": group,
            "lang": iso639_1.language_to_code(lang),
            "language": lang,
            "count": count,
        }

    @staticmethod
    def get_page_urls(page):
        """Collect next- and image-url for one manga-page"""
        _   , pos = text.extract(page, 'title="Next Chapter"', '')
        nurl, pos = text.extract(page, '<a href="', '"', pos)
        _   , pos = text.extract(page, '<div id="full_image"', '', pos)
        iurl, pos = text.extract(page, '<img src="', '"', pos)
        return nurl if "_" in nurl else None, iurl

