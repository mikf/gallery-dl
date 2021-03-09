# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaifox.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text
import json


class HentaifoxBase():
    """Base class for hentaifox extractors"""
    category = "hentaifox"
    root = "https://hentaifox.com"


class HentaifoxGalleryExtractor(HentaifoxBase, GalleryExtractor):
    """Extractor for image galleries on hentaifox.com"""
    pattern = r"(?:https?://)?(?:www\.)?hentaifox\.com(/gallery/(\d+))"
    test = ("https://hentaifox.com/gallery/56622/", {
        "pattern": r"https://i\d*\.hentaifox\.com/\d+/\d+/\d+\.jpg",
        "keyword": "bcd6b67284f378e5cc30b89b761140e3e60fcd92",
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
        cover, pos = text.extract(page, '<img src="', '"')
        data , pos = text.extract(page, "$.parseJSON('", "');", pos)
        path = "/".join(cover.split("/")[3:-1])

        result = []
        append = result.append
        extmap = {"j": "jpg", "p": "png", "g": "gif"}
        urlfmt = ("/" + path + "/{}.{}").format

        server1 = "https://i.hentaifox.com"
        server2 = "https://i2.hentaifox.com"

        for num, image in json.loads(data).items():
            ext, width, height = image.split(",")
            path = urlfmt(num, extmap[ext])
            append((server1 + path, {
                "width"    : width,
                "height"   : height,
                "_fallback": (server2 + path,),
            }))

        return result


class HentaifoxSearchExtractor(HentaifoxBase, Extractor):
    """Extractor for search results and listings on hentaifox.com"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.)?hentaifox\.com"
               r"(/(?:parody|tag|artist|character|search|group)/[^/?%#]+)")
    test = (
        ("https://hentaifox.com/parody/touhou-project/"),
        ("https://hentaifox.com/character/reimu-hakurei/"),
        ("https://hentaifox.com/artist/distance/"),
        ("https://hentaifox.com/search/touhou/"),
        ("https://hentaifox.com/group/v-slash/"),
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
