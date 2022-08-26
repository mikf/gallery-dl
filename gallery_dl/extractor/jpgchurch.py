# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?jpg\.church"


class JpgchurchExtractor(Extractor):
    """Base class for Jpgchurch extractors"""
    category = "jpgchurch"
    root = "https://jpg.church"
    directory_fmt = ("{category}", "{user}", "{album}",)
    archive_fmt = "{user}_{filename}"

    @staticmethod
    def _extract_user(page):
        return text.extract(page, 'username: "', '"')[0]

    @staticmethod
    def _extract_album(page):
        album = text.extract(page, 'Added to <a', '<span')[0]
        album = text.extract(album, '">', '</a>')[0]
        return album

    def _extract_image(self, url):
        page = self.request(url).text
        data = {
            "url": text.extract(
                page, '<meta property="og:image" content="', '" />')[0],
        }
        text.nameext_from_url(data["url"], data)
        data["user"] = self._extract_user(page)
        data["album"] = self._extract_album(page)
        return data

    def _pagination(self, url):
        while True:
            yield url
            page = self.request(url).text
            _next = text.extract(
                page, '<a data-pagination="next" href="', '" ><')[0]
            if not _next:
                return
            url = _next

    def _get_albums(self, url):
        for url in self._pagination(url):
            page = self.request(url).text
            page = text.extract_iter(
                page, '<div class="list-item-image ', 'image-container')
            for image in page:
                image = text.extract(image, '<a href="', '"')[0]
                yield image


class JpgchurchImageExtractor(JpgchurchExtractor):
    """Extractor for Jpgchurch Images"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/img/([^/?#]+)"
    test = (
        ("https://jpg.church/img/funnymeme.LecXGS", {
            "pattern": r"^https://[^/]+/.*\.(jpg|png)",
        }),
        ("https://jpg.church/img/hannahowo-00457.auCruA", {
            "pattern": r"https://simp2\.jpg\.church/hannahowo_00457\.jpg",
        }),
        ("https://jpg.church/img/hannahowo-00424.au64iA"),
    )

    def __init__(self, match):
        JpgchurchExtractor.__init__(self, match)
        self.image = match.group(1)

    def items(self):
        url = "{}/img/{}".format(self.root, self.image)
        image = self._extract_image(url)
        if not image["album"]:
            self.directory_fmt = ("{category}", "{user}",)
        yield Message.Directory, image
        yield Message.Url, image["url"], image


class JpgchurchAlbumExtractor(JpgchurchExtractor):
    """Extractor for Jpgchurch Albums"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a(?:lbum)?/([^/?#]+)(/sub)?"
    test = (
        ("https://jpg.church/album/CDilP/?sort=date_desc&page=1", {
            "count": 2,
        }),
        ("https://jpg.church/a/gunggingnsk.N9OOI", {
            "count": 114,
        }),
        ("https://jpg.church/a/101-200.aNJ6A/", {
            "count": 100,
        }),
        ("https://jpg.church/a/hannahowo.aNTdH/sub", {
            "count": 606,
        }),
    )

    def __init__(self, match):
        JpgchurchExtractor.__init__(self, match)
        self.album, self.is_sub = match.groups()

    def items(self):
        url = "{}/a/{}".format(self.root, self.album)
        data = {"_extractor": JpgchurchImageExtractor}
        if self.is_sub:
            url += "/sub"
            for album in self._get_albums(url):
                for image in self._get_albums(album):
                    yield Message.Queue, image, data
        else:
            for image in self._get_albums(url):
                yield Message.Queue, image, data


class JpgchurchUserExtractor(JpgchurchExtractor):
    """Extractor for Jpgchurch Users"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!img|a(?:lbum)?)([^/?#]+)(/albums)?"
    test = (
        ("https://jpg.church/exearco", {
            "count": 3,
        }),
        ("https://jpg.church/exearco/albums", {
            "count": 1,
        }),
    )

    def __init__(self, match):
        JpgchurchExtractor.__init__(self, match)
        self.user, self.is_album = match.groups()

    def items(self):
        url = "{}/{}".format(self.root, self.user)
        if self.is_album:
            url += "/albums"
            data = {"_extractor": JpgchurchAlbumExtractor}
            for album in self._get_albums(url):
                yield Message.Queue, album, data
        else:
            data = {"_extractor": JpgchurchImageExtractor}
            for image in self._get_albums(url):
                yield Message.Queue, image, data
