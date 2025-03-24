# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imhentai.xxx/ and mirror sites"""

from .common import GalleryExtractor, BaseExtractor, Message
from .. import text, util


class ImhentaiExtractor(BaseExtractor):
    basecategory = "IMHentai"

    def _pagination(self, url):
        prev = None
        base = self.root + "/gallery/"
        data = {"_extractor": ImhentaiGalleryExtractor}

        while True:
            page = self.request(url).text

            pos = page.find('class="ranking_list"')
            if pos >= 0:
                page = page[:pos]

            extr = text.extract_from(page)

            while True:
                gallery_id = extr('href="/gallery/', '"')
                if gallery_id == prev:
                    continue
                if not gallery_id:
                    break
                yield Message.Queue, base + gallery_id, data
                prev = gallery_id

            href = text.rextract(page, "class='page-link' href='", "'")[0]
            if not href or href == "#":
                return
            if href[0] == "/":
                if href[1] == "/":
                    href = "https:" + href
                else:
                    href = self.root + href
            url = href


BASE_PATTERN = ImhentaiExtractor.update({
    "imhentai": {
        "root": "https://imhentai.xxx",
        "pattern": r"(?:www\.)?imhentai\.xxx",
    },
    "hentaiera": {
        "root": "https://hentaiera.com",
        "pattern": r"(?:www\.)?hentaiera\.com",
    },
    "hentairox": {
        "root": "https://hentairox.com",
        "pattern": r"(?:www\.)?hentairox\.com",
    },
    "hentaifox": {
        "root": "https://hentaifox.com",
        "pattern": r"(?:www\.)?hentaifox\.com",
    },
    "hentaienvy": {
        "root": "https://hentaienvy.com",
        "pattern": r"(?:www\.)?hentaienvy\.com",
    },
    "hentaizap": {
        "root": "https://hentaizap.com",
        "pattern": r"(?:www\.)?hentaizap\.com",
    },
})


class ImhentaiGalleryExtractor(ImhentaiExtractor, GalleryExtractor):
    """Extractor for imhentai galleries"""
    pattern = BASE_PATTERN + r"/(?:gallery|view)/(\d+)"
    example = "https://imhentai.xxx/gallery/12345/"

    def __init__(self, match):
        ImhentaiExtractor.__init__(self, match)
        self.gallery_id = self.groups[-1]
        self.gallery_url = "{}/gallery/{}/".format(self.root, self.gallery_id)

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr("<h1>", "<")
        title_alt = extr('class="subtitle">', "<")
        end = "</li>" if extr('<ul class="galleries_info', ">") else "</ul>"

        data = {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(title),
            "title_alt" : text.unescape(title_alt),
            "parody"    : self._split(extr(">Parodies", end)),
            "character" : self._split(extr(">Characters", end)),
            "tags"      : self._split(extr(">Tags", end)),
            "artist"    : self._split(extr(">Artists", end)),
            "group"     : self._split(extr(">Groups", end)),
            "language"  : self._split(extr(">Languages", end)),
            "type"      : extr("href='/category/", "/"),
        }

        if data["language"]:
            data["lang"] = util.language_to_code(data["language"][0])

        return data

    def _split(self, html):
        results = []
        for tag in text.extract_iter(html, ">", "</a>"):
            badge = ("badge'>" in tag or "class='badge" in tag)
            tag = text.remove_html(tag)
            if badge:
                tag = tag.rpartition(" ")[0]
            results.append(tag)
        results.sort()
        return results

    def images(self, page):
        data = util.json_loads(text.extr(page, "$.parseJSON('", "'"))
        base = text.extr(page, 'data-src="', '"').rpartition("/")[0] + "/"
        exts = {"j": "jpg", "p": "png", "g": "gif", "w": "webp", "a": "avif"}

        results = []
        for i in map(str, range(1, len(data)+1)):
            ext, width, height = data[i].split(",")
            url = base + i + "." + exts[ext]
            results.append((url, {
                "width" : text.parse_int(width),
                "height": text.parse_int(height),
            }))
        return results


class ImhentaiTagExtractor(ImhentaiExtractor):
    """Extractor for imhentai tag searches"""
    subcategory = "tag"
    pattern = (BASE_PATTERN + r"(/(?:"
               r"artist|category|character|group|language|parody|tag"
               r")/([^/?#]+))")
    example = "https://imhentai.xxx/tag/TAG/"

    def items(self):
        url = self.root + self.groups[-2] + "/"
        return self._pagination(url)


class ImhentaiSearchExtractor(ImhentaiExtractor):
    """Extractor for imhentai search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search(/?\?[^#]+|/[^/?#]+/?)"
    example = "https://imhentai.xxx/search/?key=QUERY"

    def items(self):
        url = self.root + "/search" + self.groups[-1]
        return self._pagination(url)
