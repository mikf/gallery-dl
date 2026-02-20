# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagepond.net/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?imagepond\.net"


class ImagepondExtractor(Extractor):
    """Base class for imagepond extractors"""
    basecategory = "chevereto"
    category = "imagepond"
    root = "https://www.imagepond.net"
    directory_fmt = ("{category}", "{user}", "{album}")
    archive_fmt = "{id}"
    parent = True

    def _pagination(self, url, callback=None, pattern=None):
        page = self.request(url).text

        if callback is not None:
            callback(page)

        if pattern is not None:
            find = text.re(pattern).findall

        while True:
            if pattern is None:
                yield from text.extract_iter(
                    page, "'javascript:void(0)' : '", "'")
            else:
                yield from find(page)

            pos = page.find(' rel="next"')
            if pos < 0:
                break
            anchor = page[page.rfind("<", None, pos):page.find(">", pos)]
            url = text.extr(anchor, 'href="', '"')
            if not url:
                break
            page = self.request(text.unescape(url)).text


class ImagepondFileExtractor(ImagepondExtractor):
    subcategory = "file"
    pattern = BASE_PATTERN + r"(/(?:i(?:mg|mage)?|video)/[^/?#]+)"
    example = "https://www.imagepond.net/i/ID"

    def items(self):
        url = self.root + self.groups[0]
        response = self.request(url)
        extr = text.extract_from(response.text)

        title = text.unescape(extr('property="og:title" content="', '"'))
        type = extr('property="og:type" content="', '"')

        if type == "image":
            file = {
                "type": "image",
                "url": extr('property="og:image" content="', '"'),
                "width": text.parse_int(extr(
                    'property="og:image:width" content="', '"')),
                "height": text.parse_int(extr(
                    'property="og:image:height" content="', '"')),
            }
        else:
            file = {
                "type": "video",
                "url": extr('property="og:video" content="', '"'),
                "mime": extr('property="og:video:type" content="', '"'),
                "width": text.parse_int(extr(
                    'property="og:video:width" content="', '"')),
                "height": text.parse_int(extr(
                    'property="og:video:height" content="', '"')),
                "thumbnail": extr('property="og:image" content="', '"'),
            }
            extr('<span class="uppercase', "</span>")
            m, _, s = extr('<span>', "</span>").partition(":")
            file["duration"] = text.parse_int(m) * 60 + text.parse_int(s)

        file["id"] = response.url.rpartition("/")[2]
        file["title"] = title
        file["date"] = self.parse_datetime(extr(
            '<span class="hidden sm:inline">', '<'), "%b %d, %Y")
        file["user"] = extr('/user/', '"')

        if aid := extr("/a/", '"'):
            file["album"] = text.unescape(extr(
                "<span ", "<").partition(">")[2])
            file["album_id"] = aid
        else:
            file["album"] = file["album_id"] = ""

        text.nameext_from_url(file["url"], file)
        if "mime" not in file:
            file["mime"] = f"{file['type']}/{file['extension']}"
        yield Message.Directory, "", file
        yield Message.Url, file["url"], file


class ImagepondAlbumExtractor(ImagepondExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a(?:lbum)?/(.+)"
    example = "https://www.imagepond.net/a/ID"

    def items(self):
        url = f"{self.root}/a/{self.groups[0]}"

        data = {"_extractor": ImagepondFileExtractor}
        for self.kwdict["num"], item_url in enumerate(self._pagination(
                url, callback=self._extract_metadata_album), 1):
            yield Message.Queue, item_url, data

    def _extract_metadata_album(self, page):
        kwdict = self.kwdict
        title, pos = text.extract(page, '<h1', '<')
        kwdict["album"] = "" if title is None else text.unescape(
            title[title.find(">")+1:])
        kwdict["count"] = text.parse_int(text.extract(
            page, "<span>", " ", pos)[0])


class ImagepondUserExtractor(ImagepondExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?:user/)?(.+)"
    example = "https://www.imagepond.net/user/USER"

    def items(self):
        url = f"{self.root}/user/{self.groups[0]}"

        base = self.root + "/i/"
        data_file = {"_extractor": ImagepondFileExtractor}
        for path in self._pagination(url, pattern=r'/i/([^/?#"]+)"'):
            yield Message.Queue, base + path, data_file
