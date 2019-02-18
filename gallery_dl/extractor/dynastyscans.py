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
        page = self.request(url).text

        date, pos = text.extract(page, "class='create_at'>", "</span>")
        tags, pos = text.extract(page, "class='tags'>", "</span>", pos)
        src , pos = text.extract(page, "class='btn-group'>", "</div>", pos)
        url , pos = text.extract(page, ' src="', '"', pos)

        src = text.extract(src, 'href="', '"')[0] if "Source<" in src else ""

        return {
            "url": self.root + url,
            "image_id": text.parse_int(image_id),
            "tags": text.split_html(text.unescape(tags)),
            "date": text.remove_html(date),
            "source": text.unescape(src),
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
        info  , pos = text.extract(page, "<h3 id='chapter-title'><b>", "</b>")
        author, pos = text.extract(page, " by ", "</a>", pos)
        group , pos = text.extract(page, '"icon-print"></i> ', '</span>', pos)
        date  , pos = text.extract(page, '"icon-calendar"></i> ', '<', pos)

        match = re.match(
            (r"(?:<a[^>]*>)?([^<]+)(?:</a>)?"  # manga name
             r"(?: ch(\d+)([^:<]*))?"  # chapter info
             r"(?:: (.+))?"),  # title
            info
        )

        return {
            "manga": text.unescape(match.group(1)),
            "chapter": text.parse_int(match.group(2)),
            "chapter_minor": match.group(3) or "",
            "title": text.unescape(match.group(4) or ""),
            "author": text.remove_html(author),
            "group": (text.remove_html(group) or
                      text.extract(group, ' alt="', '"')[0] or ""),
            "date": date,
            "lang": "en",
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
    pattern = BASE_PATTERN + r"/images(?:\?([^#]+))?$"
    test = ("https://dynasty-scans.com/images?with[]=4930&with[]=5211", {
        "url": "6b570eedd8a741c2cd34fb98b22a49d772f84191",
        "keyword": "2a8f3d30584c637a0dd64ce8a0a2e81edaa6bca4",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.search_query = match.group(1)

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {}
        for image_id in self.images():
            data = self._parse_image_page(image_id)
            url = data.pop("url")
            yield Message.Url, url, text.nameext_from_url(url, data)

    def images(self):
        url = self.root + "/images?" + self.search_query
        params = {"page": 1}

        while True:
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, '"/images/', '"')
            if 'rel="next"' not in page:
                return
            params["page"] += 1


class DynastyscansImageExtractor(DynastyscansBase, Extractor):
    """Extractor for individual images on dynasty-scans.com"""
    subcategory = "image"
    directory_fmt = ("{category}", "Images")
    filename_fmt = "{image_id}.{extension}"
    pattern = BASE_PATTERN + r"/images/(\d+)"
    test = ("https://dynasty-scans.com/images/1245", {
        "url": "15e54bd94148a07ed037f387d046c27befa043b2",
        "keyword": "384889567a19d2e907ff13f65b42f9560e15172d",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.image_id = match.group(1)

    def items(self):
        data = self._parse_image_page(self.image_id)
        url = data.pop("url")

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)
