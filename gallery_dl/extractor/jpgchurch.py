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
    directory_fmt = ("{category}", "{user}",)
    archive_fmt = "{filename}"

    def __init__(self, match):
        Extractor.__init__(self, match)

    def items(self):
        for image in self.images():
            yield Message.Directory, image
            yield Message.Url, image["url"], image

    def images(self):
        """Return an iterable containing the image(s)"""

    @staticmethod
    def _extract_user(page):
        return text.extract(page, 'username: "', '"')[0]

    def _extract_image(self, url):
        page = self.request(url).text
        data = {
            "url": text.extract(
                page, '<meta property="og:image" content="', '" />')[0],
        }
        text.nameext_from_url(data["url"], data)
        data["user"] = self._extract_user(page)
        return data

    def _pagination(self, url):
        """Uses recursion to yield the next page"""
        yield url
        page = self.request(url).text
        _next = text.extract(
            page, '<a data-pagination="next" href="', '" ><')[0]
        if _next:
            url = _next
            yield from self._pagination(_next)

    def _get_images(self, url):
        for url in self._pagination(url):
            page = self.request(url).text
            album = text.extract(page, '<a data-text="album-name"', '</h1>')[0]
            album = text.extract(album, '>', '</a>')[0]
            page = text.extract_iter(
                page, '<div class="list-item-image ', 'image-container')
            for image in page:
                image = text.extract(image, '<a href="', '"')[0]
                data = self._extract_image(image)
                data["album"] = album
                yield data

    def _get_albums(self, url):
        for url in self._pagination(url):
            page = self.request(url).text
            album = text.extract(page, '<a data-text="album-name"', '</h1>')[0]
            album = text.extract(album, '>', '</a>')[0]
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
        ("https://jpg.church/img/funnymeme.LecXGS"),
    )

    def __init__(self, match):
        JpgchurchExtractor.__init__(self, match)
        self.image = match.group(1)

    def images(self):
        url = "{}/img/{}".format(self.root, self.image)
        yield self._extract_image(url)


class JpgchurchAlbumExtractor(JpgchurchExtractor):
    """Extractor for Jpgchurch Albums"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user}", "{album}",)
    pattern = BASE_PATTERN + r"/a(?:lbum)?/([^/?#]+)(/sub)?"
    test = (
        ("https://jpg.church/album/CDilP/?sort=date_desc&page=1", {
            "count": 2,
            "pattern": r"^https://[^/]+/.*\.(jpg|png)",
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
        self.album = match.group(1)
        self.is_sub = match.group(2)

    def images(self):
        url = "{}/a/{}".format(self.root, self.album)
        if self.is_sub:
            url += "/sub"
            for album in self._get_albums(url):
                yield from self._get_images(album)
        else:
            yield from self._get_images(url)


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
        self.user = match.group(1)
        self.is_album = match.group(2)

    def items(self):
        url = "{}/{}".format(self.root, self.user)
        if self.is_album:
            url += "/albums"
            data = {
                "_extractor": JpgchurchAlbumExtractor,
            }
            for album in self._get_albums(url):
                yield Message.Queue, album, data
        else:
            data = {
                "_extractor": JpgchurchImageExtractor,
            }
            for image in self._get_albums(url):
                yield Message.Queue, image, data
