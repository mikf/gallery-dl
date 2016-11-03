# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of extractors for various imagehosts"""

from .common import Extractor, Message
from .. import text
from os.path import splitext

class ImagehostImageExtractor(Extractor):
    """Base class for single-image extractors for various imagehosts"""
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    https = False
    method = "post"
    params = "simple"

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

    def items(self):
        page = self.request(self.url, method=self.method, data=self.params).text
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

#

class ImgytImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from img.yt"""
    category = "imgyt"
    pattern = [r"(?:https?://)?((?:www\.)?img\.yt/img-([a-z0-9]+)\.html)"]
    test = [("https://img.yt/img-57a2050547b97.html", {
        "url": "6801fac1ff8335bd27a1665ad27ad64cace2cd84",
        "keyword": "7548cc9915f90f5d7ffbafa079085457ae34562c",
        "content": "54592f2635674c25677c6872db3709d343cdf92f",
    })]
    https = True

    def get_info(self, page):
        url     , pos = text.extract(page, "<img class='centred' src='", "'")
        filename, pos = text.extract(page, " alt='", "'", pos)
        return url, filename + splitext(url)[1]

class RapidimgImageExtractor(ImgytImageExtractor):
    """Extractor for single images from rapidimg.net"""
    category = "rapidimg"
    pattern = [r"(?:https?://)?((?:www\.)?rapidimg\.net/img-([a-z0-9]+)\.html)"]
    test = []
    https = False

#

class ChronosImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from chronos.to"""
    category = "chronos"
    pattern = [r"(?:https?://)?((?:www\.)?chronos\.to/([a-z0-9]{12}))"]
    test = [("http://chronos.to/bdrmq7rw7v4y", {
        "url": "7fcb3fe315c94283644d25ef47a644c2dc8da944",
        "keyword": "04dbc71a1154728d01c931308184050d61c5da55",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
    https = False
    params = "complex"

    def get_info(self, page):
        url     , pos = text.extract(page, '<br><img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        return url, filename

class CoreimgImageExtractor(ChronosImageExtractor):
    """Extractor for single images from coreimg.net"""
    category = "coreimg"
    pattern = [r"(?:https?://)?((?:www\.)?coreimg\.net/([a-z0-9]{12}))"]
    test = [("http://coreimg.net/ykcl5al8uzvg", {
        "url": "2b32596a2ea66b7cc784e20f3749f75f20998d78",
        "keyword": "8d71e5b820bc7177baee33ca529c91ae4521299f",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]

class PicmaniacImageExtractor(ChronosImageExtractor):
    """Extractor for single images from pic-maniac.com"""
    category = "picmaniac"
    pattern = [r"(?:https?://)?((?:www\.)?pic-maniac\.com/([a-z0-9]{12}))"]
    test = []

#

class HosturimageImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from hosturimage.com"""
    category = "hosturimage"
    pattern = [r"(?:https?://)?((?:www\.)?hosturimage\.com/img-([a-z0-9]+)\.html)"]
    https = True

    def get_info(self, page):
        _  , pos = text.extract(page, '<div id="image_details">', '')
        url, pos = text.extract(page, "href='", "'", pos)
        return url, url

class ImageontimeImageExtractor(HosturimageImageExtractor):
    """Extractor for single images from imageontime.org"""
    category = "imageontime"
    pattern = [r"(?:https?://)?((?:www\.)?imageontime\.org/img-([a-z0-9]+)\.html)"]
    https = False

class ImguploadImageExtractor(HosturimageImageExtractor):
    """Extractor for single images from imgupload.yt"""
    category = "imgupload"
    pattern = [r"(?:https?://)?((?:www\.)?imgupload\.yt/img-([a-z0-9]+)\.html)"]
    https = True

#

class ImgspiceImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgspice.com"""
    category = "imgspice"
    pattern = [r"(?:https?://)?((?:www\.)?imgspice\.com/([^/]+))"]
    https = True
    method = "get"
    params = None

    def get_info(self, page):
        filename, pos = text.extract(page, '<td nowrap>', '</td>')
        url     , pos = text.extract(page, '<img src="', '"', pos)
        return url, filename

#

class ImgclickImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgclick.net"""
    category = "imgclick"
    pattern = [r"(?:https?://)?((?:www\.)?imgclick\.net/([^/]+))"]
    params = "complex"

    def get_info(self, page):
        url     , pos = text.extract(page, '<img  src="', '"')
        filename, pos = text.extract(page, 'alt="', '"', pos)
        return url, filename
