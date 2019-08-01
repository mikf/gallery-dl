# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://dynasty-scans.com/"""

from .common import ChapterExtractor, Extractor, Message
from .. import text
import json
import re


BASE_PATTERN = r"(?:https?://)?(?:www\.)?dynasty-scans\.com"


class DynastyscansBase():
    """Base class for dynastyscans extractors"""
    category = "dynastyscans"
    root = "https://dynasty-scans.com"

    def _parse_image_page(self, image_id):
        url = "{}/images/{}".format(self.root, image_id)
        extr = text.extract_from(self.request(url).text)

        date = extr("class='create_at'>", "</span>")
        tags = extr("class='tags'>", "</span>")
        src = extr("class='btn-group'>", "</div>")
        url = extr(' src="', '"')

        src = text.extract(src, 'href="', '"')[0] if "Source<" in src else ""

        return {
            "url"     : self.root + url,
            "image_id": text.parse_int(image_id),
            "tags"    : text.split_html(text.unescape(tags)),
            "date"    : text.remove_html(date),
            "source"  : text.unescape(src),
        }


class DynastyscansChapterExtractor(DynastyscansBase, ChapterExtractor):
    """Extractor for manga-chapters from dynasty-scans.com"""
    pattern = BASE_PATTERN + r"(/chapters/[^/?&#]+)"
    test = (
        (("http://dynasty-scans.com/chapters/"
          "hitoribocchi_no_oo_seikatsu_ch33"), {
            "url": "dce64e8c504118f1ab4135c00245ea12413896cb",
            "keyword": "1564965671ac69bb7fbc340538397f6bd0aa269b",
        }),
        (("http://dynasty-scans.com/chapters/"
          "new_game_the_spinoff_special_13"), {
            "url": "dbe5bbb74da2edcfb1832895a484e2a40bc8b538",
            "keyword": "22b35029bc65d6d95db2e2c147b0a37f2d290f29",
        }),
    )

    def metadata(self, page):
        extr = text.extract_from(page)
        match = re.match(
            (r"(?:<a[^>]*>)?([^<]+)(?:</a>)?"  # manga name
             r"(?: ch(\d+)([^:<]*))?"  # chapter info
             r"(?:: (.+))?"),  # title
            extr("<h3 id='chapter-title'><b>", "</b>"),
        )
        author = extr(" by ", "</a>")
        group = extr('"icon-print"></i> ', '</span>')

        return {
            "manga"   : text.unescape(match.group(1)),
            "chapter" : text.parse_int(match.group(2)),
            "chapter_minor": match.group(3) or "",
            "title"   : text.unescape(match.group(4) or ""),
            "author"  : text.remove_html(author),
            "group"   : (text.remove_html(group) or
                         text.extract(group, ' alt="', '"')[0] or ""),
            "date"    : extr('"icon-calendar"></i> ', '<'),
            "lang"    : "en",
            "language": "English",
        }

    def images(self, page):
        data = text.extract(page, "var pages = ", ";\n")[0]
        return [
            (self.root + img["image"], None)
            for img in json.loads(data)
        ]


class DynastyscansSearchExtractor(DynastyscansBase, Extractor):
    """Extrator for image search results on dynasty-scans.com"""
    subcategory = "search"
    directory_fmt = ("{category}", "Images")
    filename_fmt = "{image_id}.{extension}"
    archive_fmt = "i_{image_id}"
    pattern = BASE_PATTERN + r"/images/?(?:\?([^#]+))?$"
    test = (
        ("https://dynasty-scans.com/images?with[]=4930&with[]=5211", {
            "url": "6b570eedd8a741c2cd34fb98b22a49d772f84191",
            "keyword": "fa7ff94f82cdf942f7734741d758f160a6b0905a",
        }),
        ("https://dynasty-scans.com/images", {
            "range": "1",
            "count": 1,
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match.group(1) or ""

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {}
        for image_id in self.images():
            image = self._parse_image_page(image_id)
            url = image["url"]
            yield Message.Url, url, text.nameext_from_url(url, image)

    def images(self):
        url = self.root + "/images?" + self.query.replace("[]", "%5B%5D")
        params = {"page": 1}

        while True:
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, '"/images/', '"')
            if 'rel="next"' not in page:
                return
            params["page"] += 1


class DynastyscansImageExtractor(DynastyscansSearchExtractor):
    """Extractor for individual images on dynasty-scans.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/images/(\d+)"
    test = ("https://dynasty-scans.com/images/1245", {
        "url": "15e54bd94148a07ed037f387d046c27befa043b2",
        "keyword": "3b630c6139e5ff06e141541d57960f8a2957efbb",
    })

    def images(self):
        return (self.query,)
