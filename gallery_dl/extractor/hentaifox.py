# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaifox.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text


class HentaifoxBase():
    """Base class for hentaifox extractors"""
    category = "hentaifox"
    root = "https://hentaifox.com"


class HentaifoxGalleryExtractor(HentaifoxBase, GalleryExtractor):
    """Extractor for image galleries on hentaifox.com"""
    pattern = r"(?:https?://)?(?:www\.)?hentaifox\.com(/gallery/(\d+))"
    test = ("https://hentaifox.com/gallery/56622/", {
        "pattern": r"https://i\d*\.hentaifox\.com/\d+/\d+/\d+\.jpg",
        "keyword": "b7ff141331d0c7fc711ab28d45dfbb013a83d8e9",
        "count": 24,
    })

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    def metadata(self, page, split=text.split_html):
        extr = text.extract_from(page)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(extr("<h1>", "</h1>")),
            "parody"    : split(extr(">Parodies:"  , "</ul>"))[::2],
            "characters": split(extr(">Characters:", "</ul>"))[::2],
            "tags"      : split(extr(">Tags:"      , "</ul>"))[::2],
            "artist"    : split(extr(">Artists:"   , "</ul>"))[::2],
            "group"     : split(extr(">Groups:"    , "</ul>"))[::2],
            "type"      : text.remove_html(extr(">Category:", "<span")),
            "language"  : "English",
            "lang"      : "en",
        }

    def images(self, page):
        pos = page.find('id="load_all"')
        if pos >= 0:
            extr = text.extract
            load_id = extr(page, 'id="load_id" value="', '"', pos)[0]
            load_dir = extr(page, 'id="load_dir" value="', '"', pos)[0]
            load_pages = extr(page, 'id="load_pages" value="', '"', pos)[0]

            url = self.root + "/includes/thumbs_loader.php"
            data = {
                "u_id"         : self.gallery_id,
                "g_id"         : load_id,
                "img_dir"      : load_dir,
                "visible_pages": "0",
                "total_pages"  : load_pages,
                "type"         : "2",
            }
            headers = {
                "Origin": self.root,
                "Referer": self.gallery_url,
                "X-Requested-With": "XMLHttpRequest",
            }
            page = self.request(
                url, method="POST", headers=headers, data=data).text

        return [
            (url.replace("t.", "."), None)
            for url in text.extract_iter(page, 'data-src="', '"')
        ]


class HentaifoxSearchExtractor(HentaifoxBase, Extractor):
    """Extractor for search results and listings on hentaifox.com"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.)?hentaifox\.com"
               r"(/(?:parody|tag|artist|character|search)/[^/?%#]+)")
    test = (
        ("https://hentaifox.com/parody/touhou-project/"),
        ("https://hentaifox.com/character/reimu-hakurei/"),
        ("https://hentaifox.com/artist/distance/"),
        ("https://hentaifox.com/search/touhou/"),
        ("https://hentaifox.com/tag/heterochromia/", {
            "pattern": HentaifoxGalleryExtractor.pattern,
            "count": ">= 60",
            "keyword": {
                "url"       : str,
                "gallery_id": int,
                "title"     : str,
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)

    def items(self):
        yield Message.Version, 1
        for gallery in self.galleries():
            yield Message.Queue, gallery["url"], gallery

    def galleries(self):
        num = 1

        while True:
            url = "{}{}/pag/{}/".format(self.root, self.path, num)
            page = self.request(url).text

            for info in text.extract_iter(
                    page, 'class="g_title"><a href="', '</a>'):
                url, _, title = info.partition('">')

                yield {
                    "url"       : text.urljoin(self.root, url),
                    "gallery_id": text.parse_int(
                        url.strip("/").rpartition("/")[2]),
                    "title"     : text.unescape(title),
                    "_extractor": HentaifoxGalleryExtractor,
                }

            pos = page.find(">Next<")
            url = text.rextract(page, "href=", ">", pos)[0]
            if pos == -1 or "/pag" not in url:
                return
            num += 1
