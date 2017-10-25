# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of extractors for various imagehosts"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
from os.path import splitext
from urllib.parse import urljoin


class ImagehostImageExtractor(Extractor):
    """Base class for single-image extractors for various imagehosts"""
    subcategory = "image"
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


class ImgcandyImageExtractor(ImgytImageExtractor):
    """Extractor for single images from imgcandy.net"""
    category = "imgcandy"
    pattern = [(r"(?:https?://)?((?:www\.)?imgcandy\.net/img-([a-z0-9]+))"
                r"(?:_.+)?\.html")]
    test = [("http://imgcandy.net/img-57d02527efee8_test.png.html", {
        "url": "bc3c9207b10dbfe8e65ccef5b9e3194a7427b4fa",
        "keyword": "d3157ff8a33c56a8ec12931a3c098068e5a35cf5",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
    https = False

    def __init__(self, match):
        ImgytImageExtractor.__init__(self, match)
        self.url = "http://" + match.group(1) + ".html"


class RapidimgImageExtractor(ImgytImageExtractor):
    """Extractor for single images from rapidimg.net"""
    category = "rapidimg"
    pattern = [r"(?:https?://)?((?:www\.)?rapidimg\.net/"
               r"img-([a-z0-9]+)\.html)"]
    test = []
    https = False


class FapatImageExtractor(ImgytImageExtractor):
    """Extractor for single images from fapat.me"""
    category = "fapat"
    pattern = [r"(?:https?://)?((?:www\.)?fapat\.me/img-([a-z0-9]+)\.html)"]
    test = []
    https = False


class AcidimgImageExtractor(ImgytImageExtractor):
    """Extractor for single images from acidimg.cc"""
    category = "acidimg"
    pattern = [r"(?:https?://)?((?:www\.)?acidimg\.cc/img-([a-z0-9]+)\.html)"]
    test = []


class ChronosImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from chronos.to"""
    category = "chronos"
    pattern = [r"(?:https?://)?((?:www\.)?chronos\.to/([a-z0-9]{12}))"]
    test = [
        ("http://chronos.to/bdrmq7rw7v4y", {
            "url": "7fcb3fe315c94283644d25ef47a644c2dc8da944",
            "keyword": "04dbc71a1154728d01c931308184050d61c5da55",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("http://chronos.to/bdrmq7rw7v4z", {
            "exception": exception.NotFoundError,
        }),
    ]
    https = False
    params = "complex"

    def get_info(self, page):
        url, pos = text.extract(page, '<br><img src="', '"')
        if not url:
            raise exception.NotFoundError("image")
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


class ImgmaidImageExtractor(ChronosImageExtractor):
    """Extractor for single images from imgmaid.net"""
    category = "imgmaid"
    pattern = [r"(?:https?://)?((?:www\.)?imgmaid\.net/([a-z0-9]{12}))"]
    test = []
    https = True


class PicmaniacImageExtractor(ChronosImageExtractor):
    """Extractor for single images from pic-maniac.com"""
    category = "picmaniac"
    pattern = [r"(?:https?://)?((?:www\.)?pic-maniac\.com/([a-z0-9]{12}))"]
    test = []


class HosturimageImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from hosturimage.com"""
    category = "hosturimage"
    pattern = [(r"(?:https?://)?((?:www\.)?hosturimage\.com/"
                r"img-([a-z0-9]+)\.html)")]
    test = [("https://hosturimage.com/img-581ca97112bf8.html", {
        "url": "c672a3fd7fd48e5506d020aa19c4ac91ba078671",
        "keyword": "c3c94340b8e395e07b5145cf17534b5871ec8593",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
    https = True

    def get_info(self, page):
        pos = page.index("<img class='centred")
        url = text.extract(page, " src='", "'", pos)[0]
        return url, url


class ImageontimeImageExtractor(HosturimageImageExtractor):
    """Extractor for single images from imageontime.org"""
    category = "imageontime"
    pattern = [(r"(?:https?://)?((?:www\.)?imageontime\.org/"
                r"img-([a-z0-9]+)\.html)")]
    test = []
    https = False


class Img4everImageExtractor(HosturimageImageExtractor):
    """Extractor for single images from img4ever.net"""
    category = "img4ever"
    pattern = [(r"(?:https?://)?((?:www\.)?img4ever\.net/"
                r"img-([a-z0-9]+)\.html)")]
    test = []
    https = True


class ImguploadImageExtractor(HosturimageImageExtractor):
    """Extractor for single images from imgupload.yt"""
    category = "imgupload"
    pattern = [(r"(?:https?://)?((?:www\.)?imgupload\.yt/"
                r"img-([a-z0-9]+)\.html)")]
    test = []
    https = True


class ImgspotImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgspot.org"""
    category = "imgspot"
    pattern = [r"(?:https?://)?((?:www\.)?imgspot\.org/img-([a-z0-9]+)\.html)"]
    https = False

    def get_info(self, page):
        url = text.extract(page, "<img class='centred_resized' src='", "'")[0]
        return url, url


class ImgtrialImageExtractor(ImgspotImageExtractor):
    """Extractor for single images from imgtrial.com"""
    category = "imgtrial"
    pattern = [r"(?:https?://)?((?:www\.)?imgtrial\.com"
               r"/img-([a-z0-9]+)\.html)"]


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
    @cache(maxage=3*60*60)
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
        return "http://img" + url, text.unescape(filename)


class ImgtrexImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgtrex.com"""
    category = "imgtrex"
    pattern = [r"(?:https?://)?((?:www\.)?imgtrex\.com/([^/]+))"]
    test = [("http://imgtrex.com/im0ypxq0rke4/test-&<a>.png", {
        "url": "c000618bddda42bd599a590b7972c7396d19d8fe",
        "keyword": "58905795a9cd3f17d5ff024fc4d63645795ba23c",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
    params = None

    def get_info(self, page):
        filename, pos = text.extract(page, '<title>ImgTrex: ', '</title>')
        url     , pos = text.extract(page, '<br>\n<img src="', '"', pos)
        return url, filename


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
    test = [("http://www.turboimagehost.com/p/29690902/test--.png.html", {
        "url": "ada27a4e04f9ffd5ab7cd787f4559d5b3744520b",
        "keyword": "a4527f14675e4512ef317ee0401940c711fbe012",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
    params = None

    def get_info(self, page):
        needle = '<a href="http://www.turboimagehost.com"><img src="'
        url = text.extract(page, needle, '"')[0]
        return url, url
