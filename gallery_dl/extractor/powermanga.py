# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://powermanga.org/"""

from .common import Extractor, Message
from .. import text, iso639_1
import os.path
import json
import re

class PowermangaChapterExtractor(Extractor):
    """Extractor for manga-chapters from powermanga.org"""
    category = "powermanga"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03}{chapter-minor} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}"
    pattern = [
        (r"(?:https?://)?read(?:er)?\.powermanga\.org/read/"
         r"(.+/([a-z]{2})/\d+/\d+)(?:/page)?"),
        (r"(?:https?://)?(?:www\.)?(p)owermanga\.org/((?:[^-]+-)+[^-]+/?)"),
    ]
    test = [("https://read.powermanga.org/read/one_piece/en/0/803/page/1", {
        "url": "e6179c1565068f99180620281f86bdd25be166b4",
        "keyword": "1c8593087f4a2e3343966a2900fc67be8e6401f1",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        if match.group(1) == "p":
            page = self.request("https://powermanga.org/" + match.group(2)).text
            pos = page.index("class='small-button smallblack'>Download</a>")
            url = text.extract(page, "<a href='", "'", pos)[0]
            match = re.match(self.pattern[0], url)
        self.part = match.group(1)
        self.lang = match.group(2)
        extra = "er" if "://reader" in match.string else ""
        self.url_base = "https://read" + extra + ".powermanga.org/read/"

    def items(self):
        yield Message.Version, 1
        data, pages = self.get_job_metadata()
        yield Message.Directory, data
        for page_index, page_data in enumerate(pages, 1):
            name, ext = os.path.splitext(page_data["filename"])
            page_data.update(data)
            page_data["page"] = page_index
            page_data["name"] = name
            page_data["extension"] = ext[1:]
            yield Message.Url, "http" + page_data["url"][4:], page_data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request(self.url_base + self.part, encoding="utf-8").text
        _        , pos = text.extract(page, '<h1 class="tbtitle dnone">', '')
        manga    , pos = text.extract(page, 'title="', '"', pos)
        chapter  , pos = text.extract(page, '">', '</a>', pos)
        json_data, pos = text.extract(page, 'var pages = ', ';', pos)
        match = re.match(r"(\w+ (\d+)([^:+]*)(?:: (.*))?|[^:]+)", chapter)
        return {
            "manga": text.unescape(manga),
            "chapter": match.group(2) or match.group(1),
            "chapter-minor": match.group(3) or "",
            "lang": self.lang,
            "language": iso639_1.code_to_language(self.lang),
            "title": text.unescape(match.group(4) or ""),
        }, json.loads(json_data)
