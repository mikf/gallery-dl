# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://www.mangamint.com/"""

from .common import Extractor, Message
from .. import text, exception
import re


class MangamintExtractor(Extractor):
    """Base class for mangamint extractors"""
    category = "mangamint"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor}"]
    filename_fmt = ("{manga}_c{chapter:>03}{chapter-minor}_"
                    "{page:>03}.{extension}")
    url_base = "https://www.mangamint.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = self.url_base + match.group(1)


class MangamintMangaExtractor(MangamintExtractor):
    """Extractor for mangas from mangamint.com"""
    subcategory = "manga"
    pattern = [(r"(?:https?://)?(?:www\.)?mangamint\.com"
                r"(/manga/[^/\?]+)")]
    test = [
        ("www.mangamint.com/manga/mushishi-manga", {
            "url": "df7a1f4224d23e392ec09d4c7bbd4fbc873327d0",
        }),
        ("https://www.mangamint.com/manga/mushishi", {
            "exception": exception.NotFoundError,
        }),
    ]

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, self.url_base + chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        params = {"page": 0}
        chapters = []
        while True:
            response = self.session.get(self.url, params=params)
            if response.status_code == 404:
                raise exception.NotFoundError("manga")
            page = response.text
            table, pos = text.extract(
                page, '<table class="sticky-enabled">', '</table>')
            chapters.extend(text.extract_iter(table, '<a href="', '"'))
            if page.find("pager-last", pos) == -1:
                break
            params["page"] += 1
        return reversed(chapters)


class MangamintChapterExtractor(MangamintExtractor):
    """Extractor for manga-chapters from mangamint.com"""
    subcategory = "chapter"
    pattern = [(r"(?:https?://)?(?:www\.)?mangamint\.com"
                r"(/[^/\?]+-\d+(?:[^/\?]+)?)")]
    test = [
        ("http://www.mangamint.com/mushishi-1", {
            "url": "f854310a15c6b6ad7e4a2a923a612756a62c0b3e",
            "keyword": "de9ea839d231cb9f1590a2a93ca9ab2f8743b39d",
        }),
        ("https://www.mangamint.com/gosu-551", {
            "url": "56a16d2560830a4e53bfe60590c21b0a1c4069e7",
            "keyword": "f862c1d927d331a016e306305534d38d877aa3fe",
            "content": "8d7ae90e932dc2fa48163497fca78729b2c7a759",
        }),
        ("https://www.mangamint.com/gosu-552", {
            "exception": exception.NotFoundError,
        }),
    ]

    def items(self):
        response = self.session.get(self.url)
        if response.status_code == 404:
            raise exception.NotFoundError("chapter")
        page = response.text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            if url.startswith("http:"):
                url = "https:" + url[5:]
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        manga, pos = text.extract(page, 'selected="selected">', '<')
        chid , pos = text.extract(page, 'id="node-', '"', pos)
        match = re.match(r"(.+) (\d+)([^ ]*)$", manga)
        return {
            "manga": match.group(1),
            "chapter": match.group(2),
            "chapter-minor": match.group(3),
            "chapter-id": chid,
            "lang": "en",
            "language": "English",
        }

    def get_image_urls(self, page):
        """Extract list of all image-urls for a manga chapter"""
        params = {
            "manga_page": 0,
            "form_id": "select_similar_node_widget",
        }
        e = text.extract
        params["select_node"]  , pos = e(page, r'"identifier":"node\/', '"')
        _                      , pos = e(page, '>All pages<', '', pos)
        params["howmany"]      , pos = e(page, 'value="', '"', pos-25)
        _                      , pos = e(page, 'name="form_build_id"', '', pos)
        params["form_build_id"], pos = e(page, 'value="', '"', pos)
        url = self.url_base + "/many/callback"
        page = self.request(url, method="post", data=params).json()["data"]
        return list(text.extract_iter(page, r'<img src ="', r'"'))
