# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://hitomi.la/"""

from .common import Extractor, Message
from .. import text, util
import string


class HitomiGalleryExtractor(Extractor):
    """Extractor for image galleries from hitomi.la"""
    category = "hitomi"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>03}_{name}.{extension}"
    pattern = [r"(?:https?://)?hitomi\.la/(?:galleries|reader)/(\d+)\.html"]
    test = [("https://hitomi.la/galleries/867789.html", {
        "url": "e42a47dfadda93e4bf37e82b1dc9ad29edfa9130",
        "keyword": "c007cd41229d727b2ced3b364350561444738351",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)

    def items(self):
        url = "https://hitomi.la/galleries/" + self.gid + ".html"
        page = self.request(url).text
        data = self.get_job_metadata(page)
        images = self.get_image_urls(page)
        data["count"] = len(images)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(images, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        group = ""
        gtype = ""
        series = ""
        _     , pos = text.extract(page, '<h1><a href="/reader/', '')
        title , pos = text.extract(page, '.html">', "</a>", pos)
        _     , pos = text.extract(page, '<li><a href="/artist/', '', pos)
        artist, pos = text.extract(page, '.html">', '</a>', pos)
        test  , pos = text.extract(page, '<li><a href="/group/', '', pos)
        if test is not None:
            group , pos = text.extract(page, '.html">', '</a>', pos)
        test  , pos = text.extract(page, '<a href="/type/', '', pos)
        if test is not None:
            gtype , pos = text.extract(page, '.html">', '</a>', pos)
        _     , pos = text.extract(page, '<tdLanguage</td>', '', pos)
        lang  , pos = text.extract(page, '.html">', '</a>', pos)
        test  , pos = text.extract(page, '<a href="/series/', '', pos)
        if test is not None:
            series, pos = text.extract(page, '.html">', '</a>', pos)
        lang = lang.capitalize()
        return {
            "gallery_id": self.gid,
            "title": " ".join(title.split()),
            "artist": string.capwords(artist),
            "group": string.capwords(group),
            "type": gtype.strip().capitalize(),
            "lang": util.language_to_code(lang),
            "language": lang,
            "series": string.capwords(series),
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        return [
            "https://la.hitomi.la/galleries/" + urlpart
            for urlpart in text.extract_iter(
                page, "'//tn.hitomi.la/smalltn/", ".jpg',"
            )
        ]
