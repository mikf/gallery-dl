# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaifox.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util


class HentaifoxBase():
    """Base class for hentaifox extractors"""
    category = "hentaifox"
    root = "https://hentaifox.com"


class HentaifoxGalleryExtractor(HentaifoxBase, GalleryExtractor):
    """Extractor for image galleries on hentaifox.com"""
    pattern = r"(?:https?://)?(?:www\.)?hentaifox\.com(/gallery/(\d+))"
    example = "https://hentaifox.com/gallery/12345/"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    @staticmethod
    def _split(txt):
        return [
            text.remove_html(tag.partition(">")[2], "", "")
            for tag in text.extract_iter(
                txt, "class='tag_btn", "<span class='t_badge")
        ]

    def metadata(self, page):
        extr = text.extract_from(page)
        split = self._split

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "parody"    : split(extr(">Parodies:"  , "</ul>")),
            "characters": split(extr(">Characters:", "</ul>")),
            "tags"      : split(extr(">Tags:"      , "</ul>")),
            "artist"    : split(extr(">Artists:"   , "</ul>")),
            "group"     : split(extr(">Groups:"    , "</ul>")),
            "type"      : text.remove_html(extr(">Category:", "<span")),
            "title"     : text.unescape(extr(
                'id="gallery_title" value="', '"')),
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

        for num, image in util.json_loads(data).items():
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
    example = "https://hentaifox.com/tag/TAG/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)

    def items(self):
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
