# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of extractors for various imagehosts"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import memcache
from os.path import splitext
from urllib.parse import urljoin


class ImagehostImageExtractor(Extractor):
    """Base class for single-image extractors for various imagehosts"""
    subcategory = "image"
    archive_fmt = "{token}"
    https = False
    method = "post"
    params = "simple"
    cookies = None

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = ("https://" if self.https else "http://") + match.group(1)
        self.token = match.group(2)
        if self.params == "simple":
            self.params = {
                "imgContinue": "Continue+to+image+...+",
            }
        elif self.params == "complex":
            self.params = {
                "op": "view",
                "id": self.token,
                "pre": "1",
                "adb": "1",
                "next": "Continue+to+image+...+",
            }
        else:
            self.params = {}
            self.method = "get"

    def items(self):
        page = self.request(self.url, method=self.method, data=self.params,
                            cookies=self.cookies).text
        url, filename = self.get_info(page)
        data = text.nameext_from_url(filename, {"token": self.token})
        if self.https and url.startswith("http:"):
            url = "https:" + url[5:]
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data

    def get_info(self, page):
        """Find image-url and string to get filename from"""
        return "url", "filename"


class ImgytImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from img.yt"""
    category = "imgyt"
    pattern = [r"(?:https?://)?((?:www\.)?img\.yt/img-([a-z0-9]+)\.html)"]
    test = [
        ("https://img.yt/img-57a2050547b97.html", {
            "url": "6801fac1ff8335bd27a1665ad27ad64cace2cd84",
            "keyword": "7548cc9915f90f5d7ffbafa079085457ae34562c",
            "content": "54592f2635674c25677c6872db3709d343cdf92f",
        }),
        ("https://img.yt/img-57a2050547b98.html", {
            "exception": exception.NotFoundError,
        }),
    ]
    https = True

    def get_info(self, page):
        url, pos = text.extract(page, "<img class='centred' src='", "'")
        if not url:
            raise exception.NotFoundError("image")
        filename, pos = text.extract(page, " alt='", "'", pos)
        filename = (filename + splitext(url)[1]) if filename else url
        return url, filename


class AcidimgImageExtractor(ImgytImageExtractor):
    """Extractor for single images from acidimg.cc"""
    category = "acidimg"
    pattern = [r"(?:https?://)?((?:www\.)?acidimg\.cc/img-([a-z0-9]+)\.html)"]
    test = []


class ImagevenueImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imagevenue.com"""
    category = "imagevenue"
    pattern = [(r"(?:https?://)?(img\d+\.imagevenue\.com/"
                r"img\.php\?image=(\d+)_[^&#]+)")]
    params = None

    def get_info(self, page):
        url = text.extract(page, 'SRC="', '"')[0]
        url = urljoin(self.url, url)
        return url, url


class ImagetwistImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imagetwist.com"""
    category = "imagetwist"
    pattern = [r"(?:https?://)?((?:www\.)?imagetwist\.com/([a-z0-9]{12}))"]
    test = [("http://imagetwist.com/4e46hv31tu0q/test.jpg", {
        "url": "c999dc1a5dec0525ac9eb8c092f173dfe6dba0b0",
        "keyword": "30dd34dcb06b5b51c6cfff199c610b24edb7b9bc",
        "content": "96b1fd099b06faad5879fce23a7e4eb8290d8810",
    })]
    https = True
    params = None

    @property
    @memcache(maxage=3*60*60)
    def cookies(self):
        return self.request(self.url).cookies

    def get_info(self, page):
        url     , pos = text.extract(page, 'center;"><img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        return url, filename


class ImgspiceImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgspice.com"""
    category = "imgspice"
    pattern = [r"(?:https?://)?((?:www\.)?imgspice\.com/([^/]+))"]
    test = [("https://imgspice.com/zop38mvvq29u/", {
        "url": "a45833733c02b64d105363ffd8fd19f06992a2f7",
    })]
    https = True
    params = None

    def get_info(self, page):
        filename, pos = text.extract(page, '<td nowrap>', '</td>')
        url     , pos = text.extract(page, '<img src="https://img', '"', pos)
        return "https://img" + url, text.unescape(filename)


class PixhostImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from pixhost.org"""
    category = "pixhost"
    pattern = [(r"(?:https?://)?((?:www\.)?pixhost\.org/show/"
                r"\d+/(\d+)_[^/]+)")]
    https = True
    params = None
    cookies = {"pixhostads": "1", "pixhosttest": "1"}

    def get_info(self, page):
        url     , pos = text.extract(page, "class=\"image-img\" src=\"", "\"")
        filename, pos = text.extract(page, "alt=\"", "\"", pos)
        return url, filename


class PostimgImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from postimg.org"""
    category = "postimg"
    pattern = [(r"(?:https?://)?((?:www\.)?(?:postimg|pixxxels)\.org/"
                r"image/([^/]+)/?)")]
    https = True
    params = None

    def get_info(self, page):
        url = "https:" + text.extract(page, 'data-full="', '"')[0]
        return url, url


class TurboimagehostImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from turboimagehost.com"""
    category = "turboimagehost"
    pattern = [(r"(?:https?://)?((?:www\.)?turboimagehost\.com/p/(\d+)"
                r"/[^/]+\.html)")]
    test = [("https://www.turboimagehost.com/p/29690902/test--.png.html", {
        "url": "ada27a4e04f9ffd5ab7cd787f4559d5b3744520b",
        "keyword": "a4527f14675e4512ef317ee0401940c711fbe012",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
    https = True
    params = None

    def get_info(self, page):
        needle = '://www.turboimagehost.com"><img src="'
        url = text.extract(page, needle, '"')[0]
        return url, url
