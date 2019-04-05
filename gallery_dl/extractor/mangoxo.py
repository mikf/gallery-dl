# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.mangoxo.com/"""

from .common import Extractor, Message
from .. import text


class MangoxoBase():
    """Base class for mangoxo extractors"""
    category = "mangoxo"
    root = "https://www.mangoxo.com"

    @staticmethod
    def _total_pages(page):
        return text.parse_int(text.extract(page, "total :", ",")[0])


class MangoxoAlbumExtractor(MangoxoBase, Extractor):
    """Extractor for albums on mangoxo.com"""
    subcategory = "album"
    filename_fmt = "{album[id]}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{channel[name]}", "{album[name]}")
    archive_fmt = "{album[id]}_{num}"
    pattern = r"(?:https?://)?(?:www\.)?mangoxo\.com/album/(\w+)"
    test = ("https://www.mangoxo.com/album/lzVOv1Q9", {
        "url": "ad921fe62663b06e7d73997f7d00646cab7bdd0d",
        "keyword": {
            "channel": {
                "id": "QeYKRkO0",
                "name": "美女图社",
                "cover": str,
            },
            "album": {
                "id": "lzVOv1Q9",
                "name": "池永康晟 Ikenaga Yasunari 透出古朴气息的日本美女人像画作",
                "date": "2019.3.22 14:42",
                "description": str,
            },
            "num": int,
            "count": 65,
        },
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        url = "{}/album/{}/".format(self.root, self.album_id)
        page = self.request(url).text
        data = self.metadata(page)
        imgs = self.images(url, page)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], image in enumerate(imgs, 1):
            yield Message.Url, image, text.nameext_from_url(image, data)

    def metadata(self, page):
        """Return general metadata"""
        title, pos = text.extract(page, '<title>', '</title>')
        count, pos = text.extract(page, 'id="pic-count">', '<', pos)
        cover, pos = text.extract(page, ' src="', '"', pos)
        cid  , pos = text.extract(page, '//www.mangoxo.com/channel/', '"', pos)
        cname, pos = text.extract(page, '>', '<', pos)
        date , pos = text.extract(page, '</i>', '<', pos)
        descr, pos = text.extract(page, '<pre>', '</pre>', pos)

        return {
            "channel": {
                "id": cid,
                "name": text.unescape(cname),
                "cover": cover,
            },
            "album": {
                "id": self.album_id,
                "name": text.unescape(title),
                "date": date.strip(),
                "description": text.unescape(descr),
            },
            "count": text.parse_int(count),
        }

    def images(self, url, page):
        """Generator; Yields all image URLs"""
        total = self._total_pages(page)
        num = 1

        while True:
            yield from text.extract_iter(
                page, 'class="lightgallery-item" href="', '"')
            if num >= total:
                return
            num += 1
            page = self.request(url + str(num)).text


class MangoxoChannelExtractor(MangoxoBase, Extractor):
    """Extractor for all albums on a mangoxo channel"""
    subcategory = "channel"
    pattern = r"(?:https?://)?(?:www\.)?mangoxo\.com/channel/(\w+)"
    test = ("https://www.mangoxo.com/channel/QeYKRkO0", {
        "pattern": MangoxoAlbumExtractor.pattern,
        "range": "1-30",
        "count": "> 20",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.channel_id = match.group(1)

    def items(self):
        yield Message.Version, 1
        url = "{}/channel/{}/".format(self.root, self.channel_id)
        num = total = 1

        while True:
            page = self.request(url + str(num)).text

            for album in text.extract_iter(
                    page, 'class="orange link" href="', '"'):
                yield Message.Queue, album, {}

            if num == 1:
                total = self._total_pages(page)
            if num >= total:
                return
            num += 1
