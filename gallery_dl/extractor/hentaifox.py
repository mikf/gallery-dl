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
        "count": 24,
        "keyword": "38f8517605feb6854d48833297da6b05c6541b69",
    })

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    def metadata(self, page, split=text.split_html):
        extr = text.extract_from(page)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(extr("<h1>", "</h1>")),
            "parody"    : split(extr(">Parodies:"  , "</a></span>"))[::2],
            "characters": split(extr(">Characters:", "</a></span>"))[::2],
            "tags"      : split(extr(">Tags:"      , "</a></span>"))[::2],
            "artist"    : split(extr(">Artists:"   , "</a></span>"))[::2],
            "group"     : split(extr(">Groups:"    , "</a></span>"))[::2],
            "type"      : text.remove_html(extr(">Category:", "</a></span>")),
            "language"  : "English",
            "lang"      : "en",
        }

    def images(self, page):
        return [
            (text.urljoin(self.root, url.replace("t.", ".")), None)
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
        ("https://hentaifox.com/tag/full-colour/", {
            "pattern": HentaifoxGalleryExtractor.pattern,
            "count": ">= 40",
            "keyword": {
                "url": str,
                "gallery_id": int,
                "thumbnail": r"re:https://i\d*.hentaifox.com/\d+/\d+/thumb\.",
                "title": str,
                "tags": list,
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
        url = "{}/{}/".format(self.root, self.path)

        while True:
            page = self.request(url).text
            info, gpos = text.extract(
                page, 'class="galleries_overview">', 'class="clear">')

            for ginfo in text.extract_iter(info, '<div class="item', '</a>'):
                tags , pos = text.extract(ginfo, '', '"')
                url  , pos = text.extract(ginfo, 'href="', '"', pos)
                title, pos = text.extract(ginfo, 'alt="', '"', pos)
                thumb, pos = text.extract(ginfo, 'src="', '"', pos)

                yield {
                    "url": text.urljoin(self.root, url),
                    "gallery_id": text.parse_int(
                        url.strip("/").rpartition("/")[2]),
                    "thumbnail": text.urljoin(self.root, thumb),
                    "title": text.unescape(title),
                    "tags": tags.split(),
                    "_extractor": HentaifoxGalleryExtractor,
                }

            pos = page.find('class="current"', gpos)
            url = text.extract(page, 'href="', '"', pos)[0]
            if pos == -1 or "/pag" not in url:
                return
            url = text.urljoin(self.root, url)
