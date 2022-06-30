# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?jpg\.church"


class JpgchurchImageExtractor(Extractor):
    """Base Extractor for Jpgchurch Images"""
    category = "Jpgchurch"
    subcategory = "image"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{filename}"
    pattern = BASE_PATTERN + r"/img/([\w\d\-\.]+)"
    root = "https://jpg.church"
    test = ("https://jpg.church/img/funnymeme.LecXGS",)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.image = match.group(1)

    def items(self):
        data = self.metadata()
        for image in self.images():
            if "album" in image or "user" in image:
                data.update(image)
            yield Message.Directory, data
            yield Message.Url, image["url"], image

    def metadata(self):
        """Return general metadata"""
        return {}

    def images(self):
        """Return an iterable containing the image(s)"""
        url = "{}/img/{}".format(self.root, self.image)
        return [self._get_images(url)]

    def _get_images(self, url):
        page = self.request(url).text
        data = self._extract_image(page)
        data.update({
            "user": data["user"].split("/")[-1],
            "extension": text.ext_from_url(data["url"])
        })
        return data

    @staticmethod
    def _extract_image(page):
        _page = text.extract(
            page,
            '<div class="header-content-right">', '<span class="user-image')[0]
        return text.extract_all(_page, (
            ('url', '<a href="', '" download='),
            ('filename', '"', '" class'),
            ('user', '<a href="', '" class="user-image">')))[0]


class JpgchurchAlbumExtractor(JpgchurchImageExtractor, Extractor):
    """Extractor for Jpgchurch Albums"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user}", "{album}",)
    pattern = BASE_PATTERN + r"/a(?:lbum)?/([\w\d\-\.]+)"
    test = ("https://jpg.church/album/CDilP/?sort=date_desc&page=1",)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album = match.group(1).split('.')[-1]

    def metadata(self):
        return {"album": self.album}

    def images(self):
        url = "{}/a/{}".format(self.root, self.album)
        for _url in self._get_album_images(url):
            yield self._get_images(_url)

    def _pagination(self, url):
        """Uses recursion to yield the next page"""
        yield url
        page = self.request(url).text
        _next = text.extract(
            page, '<a data-pagination="next" href="', '" ><')[0]
        if _next:
            url = _next
            yield from self._pagination(_next)

    def _get_album_images(self, url):
        for _url in self._pagination(url):
            page = self.request(_url).text
            _page = text.extract_iter(
                page, '<div class="list-item-image ', 'image-container')
            for image in _page:
                yield text.extract(image, '<a href="', '" class')[0]


class JpgchurchUserExtractor(JpgchurchAlbumExtractor, Extractor):
    """Extractor for Jpgchurch Users"""
    subcategory = "user"
    directory_fmt = ("{category}", "{user}",)
    pattern = BASE_PATTERN + r"/(?!img|a(?:lbum)?)([\w\d\-\.]+)"
    test = ("https://jpg.church/exearco",)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def metadata(self):
        return {"user": self.user}

    def images(self):
        url = "{}/{}".format(self.root, self.user)
        for _url in self._get_album_images(url):
            yield self._get_images(_url)
