# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://www.mangamint.com/"""

from .common import Extractor, Message
from .. import text
import re

class MangamintMangaExtractor(Extractor):
    """Extractor for mangas from mangamint.com"""
    category = "mangamint"
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?mangamint\.com(/manga/[^\?]+-manga)"]
    test = [("www.mangamint.com/manga/mushishi-manga", {
        "url": "df7a1f4224d23e392ec09d4c7bbd4fbc873327d0",
    })]
    url_base = "https://www.mangamint.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.part = match.group(1)

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, self.url_base + chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        url = self.url_base + self.part
        params = {"page": 0}
        chapters = []
        while True:
            page = self.request(url, params=params).text
            table = text.extract(page, '<table class="sticky-enabled">', '</table>')[0]
            chapters.extend(text.extract_iter(table, '<a href="', '"'))
            if re.match(r".+-0*1$", chapters[-1]):
                break
            params["page"] += 1
        return reversed(chapters)


class MangamintChapterExtractor(Extractor):
    """Extractor for manga-chapters from mangamint.com"""
    category = "mangamint"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor}"]
    filename_fmt = "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?mangamint\.com/([^\?]+-(\d+))"]
    test = [("http://www.mangamint.com/mushishi-1", {
        "url": "337f46c4dab50f544e9196ced723ac8f70400dd0",
        "keyword": "de9ea839d231cb9f1590a2a93ca9ab2f8743b39d",
    })]

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
        manga, pos = text.extract(page, '"title":"', '"')
        chid , pos = text.extract(page, r'"identifier":"node\/', '"', pos)
        match = re.match(r"(.+) (\d+)(\.\d+)?$", manga)
        return {
            "manga": match.group(1),
            "chapter": match.group(2),
            "chapter-minor": match.group(3) or "",
            "chapter-id": chid,
            # "title": "",
            "lang": "en",
            "language": "English",
        }

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
        url = "https://www.mangamint.com/many/callback"
        page = self.request(url, method="post", data=params).json()["data"]
        imgs = []
        pos = 0
        while True:
            url, pos = text.extract(page, r'<img src ="', r'"', pos)
            if not url:
                return imgs
            imgs.append(url)
