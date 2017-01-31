# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from http://powermanga.org/"""

from .foolslide import FoolslideChapterExtractor
from .. import text
import re


class PowermangaChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from powermanga.org"""
    category = "powermanga"
    pattern = [
        (r"(?:https?://)?read(?:er)?\.powermanga\.org/read/"
         r"(.+/([a-z]{2})/\d+/\d+)(?:/page)?"),
        (r"(?:https?://)?(?:www\.)?(p)owermanga\.org/((?:[^-]+-)+[^-]+/?)"),
    ]
    test = [("https://read.powermanga.org/read/one_piece/en/0/803/page/1", {
        "url": "e6179c1565068f99180620281f86bdd25be166b4",
        "keyword": "51cabad8995727334e5ca9773c18d709b3868f02",
    })]

    def __init__(self, match):
        if match.group(1) == "p":
            url = "https://powermanga.org/" + match.group(2)
            page = self.request(url).text
            pos = page.index("class='small-button smallblack'>Download</a>")
            url = text.extract(page, "<a href='", "'", pos)[0]
            match = re.match(self.pattern[0], url)
        extra = "er" if "://reader" in match.string else ""
        url = "https://read" + extra + ".powermanga.org/read/" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
