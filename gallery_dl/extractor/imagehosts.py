# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of extractors for various imagehosts"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import memcache
from os.path import splitext


class ImagehostImageExtractor(Extractor):
    """Base class for single-image extractors for various imagehosts"""
    basecategory = "imagehost"
    subcategory = "image"
    archive_fmt = "{token}"
    _https = True
    _params = None
    _cookies = None
    _encoding = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_url = "http{}://{}".format(
            "s" if self._https else "", match.group(1))
        self.token = match.group(2)

        if self._params == "simple":
            self._params = {
                "imgContinue": "Continue+to+image+...+",
            }
        elif self._params == "complex":
            self._params = {
                "op": "view",
                "id": self.token,
                "pre": "1",
                "adb": "1",
                "next": "Continue+to+image+...+",
            }

    def items(self):
        page = self.request(
            self.page_url,
            method=("POST" if self._params else "GET"),
            data=self._params,
            cookies=self._cookies,
            encoding=self._encoding,
        ).text

        url, filename = self.get_info(page)
        data = text.nameext_from_url(filename, {"token": self.token})
        data.update(self.metadata(page))
        if self._https and url.startswith("http:"):
            url = "https:" + url[5:]

        yield Message.Directory, data
        yield Message.Url, url, data

    def get_info(self, page):
        """Find image-url and string to get filename from"""

    def metadata(self, page):
        """Return additional metadata"""
        return ()


class ImxtoImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imx.to"""
    category = "imxto"
    pattern = (r"(?:https?://)?(?:www\.)?((?:imx\.to|img\.yt)"
               r"/(?:i/|img-)(\w+)(\.html)?)")
    example = "https://imx.to/i/ID"
    _params = "simple"
    _encoding = "utf-8"

    def __init__(self, match):
        ImagehostImageExtractor.__init__(self, match)
        if "/img-" in self.page_url:
            self.page_url = self.page_url.replace("img.yt", "imx.to")
            self.url_ext = True
        else:
            self.url_ext = False

    def get_info(self, page):
        url, pos = text.extract(
            page, '<div style="text-align:center;"><a href="', '"')
        if not url:
            raise exception.NotFoundError("image")
        filename, pos = text.extract(page, ' title="', '"', pos)
        if self.url_ext and filename:
            filename += splitext(url)[1]
        return url, filename or url

    def metadata(self, page):
        extr = text.extract_from(page, page.index("[ FILESIZE <"))
        size = extr(">", "</span>").replace(" ", "")[:-1]
        width, _, height = extr(">", " px</span>").partition("x")
        return {
            "size"  : text.parse_bytes(size),
            "width" : text.parse_int(width),
            "height": text.parse_int(height),
            "hash"  : extr(">", "</span>"),
        }


class ImxtoGalleryExtractor(ImagehostImageExtractor):
    """Extractor for image galleries from imx.to"""
    category = "imxto"
    subcategory = "gallery"
    pattern = r"(?:https?://)?(?:www\.)?(imx\.to/g/([^/?#]+))"
    example = "https://imx.to/g/ID"

    def items(self):
        page = self.request(self.page_url).text
        title, pos = text.extract(page, '<div class="title', '<')
        data = {
            "_extractor": ImxtoImageExtractor,
            "title": text.unescape(title.partition(">")[2]).strip(),
        }

        for url in text.extract_iter(page, "<a href=", " ", pos):
            yield Message.Queue, url.strip("\"'"), data


class AcidimgImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from acidimg.cc"""
    category = "acidimg"
    pattern = r"(?:https?://)?((?:www\.)?acidimg\.cc/img-([a-z0-9]+)\.html)"
    example = "https://acidimg.cc/img-abc123.html"
    _params = "simple"
    _encoding = "utf-8"

    def get_info(self, page):
        url, pos = text.extract(page, "<img class='centred' src='", "'")
        if not url:
            url, pos = text.extract(page, '<img class="centred" src="', '"')
            if not url:
                raise exception.NotFoundError("image")

        filename, pos = text.extract(page, "alt='", "'", pos)
        if not filename:
            filename, pos = text.extract(page, 'alt="', '"', pos)

        return url, (filename + splitext(url)[1]) if filename else url


class ImagevenueImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imagevenue.com"""
    category = "imagevenue"
    pattern = (r"(?:https?://)?((?:www|img\d+)\.imagevenue\.com"
               r"/([A-Z0-9]{8,10}|view/.*|img\.php\?.*))")
    example = "https://www.imagevenue.com/ME123456789"

    def get_info(self, page):
        pos = page.index('class="card-body')
        url, pos = text.extract(page, '<img src="', '"', pos)
        if url.endswith("/loader.svg"):
            url, pos = text.extract(page, '<img src="', '"', pos)
        filename, pos = text.extract(page, 'alt="', '"', pos)
        return url, text.unescape(filename)


class ImagetwistImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imagetwist.com"""
    category = "imagetwist"
    pattern = (r"(?:https?://)?((?:www\.|phun\.)?"
               r"image(?:twist|haha)\.com/([a-z0-9]{12}))")
    example = "https://imagetwist.com/123456abcdef/NAME.EXT"

    @property
    @memcache(maxage=3*3600)
    def _cookies(self):
        return self.request(self.page_url).cookies

    def get_info(self, page):
        url     , pos = text.extract(page, '<img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        return url, filename


class ImagetwistGalleryExtractor(ImagehostImageExtractor):
    """Extractor for galleries from imagetwist.com"""
    category = "imagetwist"
    subcategory = "gallery"
    pattern = (r"(?:https?://)?((?:www\.|phun\.)?"
               r"image(?:twist|haha)\.com/(p/[^/?#]+/\d+))")
    example = "https://imagetwist.com/p/USER/12345/NAME"

    def items(self):
        data = {"_extractor": ImagetwistImageExtractor}
        root = self.page_url[:self.page_url.find("/", 8)]
        page = self.request(self.page_url).text
        gallery = text.extr(page, 'class="gallerys', "</div")
        for path in text.extract_iter(gallery, ' href="', '"'):
            yield Message.Queue, root + path, data


class ImgspiceImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgspice.com"""
    category = "imgspice"
    pattern = r"(?:https?://)?((?:www\.)?imgspice\.com/([^/?#]+))"
    example = "https://imgspice.com/ID/NAME.EXT.html"

    def get_info(self, page):
        pos = page.find('id="imgpreview"')
        if pos < 0:
            raise exception.NotFoundError("image")
        url , pos = text.extract(page, 'src="', '"', pos)
        name, pos = text.extract(page, 'alt="', '"', pos)
        return url, text.unescape(name)


class PixhostImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from pixhost.to"""
    category = "pixhost"
    pattern = (r"(?:https?://)?((?:www\.)?pixhost\.(?:to|org)"
               r"/show/\d+/(\d+)_[^/?#]+)")
    example = "https://pixhost.to/show/123/12345_NAME.EXT"
    _cookies = {"pixhostads": "1", "pixhosttest": "1"}

    def get_info(self, page):
        url     , pos = text.extract(page, "class=\"image-img\" src=\"", "\"")
        filename, pos = text.extract(page, "alt=\"", "\"", pos)
        return url, filename


class PixhostGalleryExtractor(ImagehostImageExtractor):
    """Extractor for image galleries from pixhost.to"""
    category = "pixhost"
    subcategory = "gallery"
    pattern = (r"(?:https?://)?((?:www\.)?pixhost\.(?:to|org)"
               r"/gallery/([^/?#]+))")
    example = "https://pixhost.to/gallery/ID"

    def items(self):
        page = text.extr(self.request(
            self.page_url).text, 'class="images"', "</div>")
        data = {"_extractor": PixhostImageExtractor}
        for url in text.extract_iter(page, '<a href="', '"'):
            yield Message.Queue, url, data


class PostimgImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from postimages.org"""
    category = "postimg"
    pattern = (r"(?:https?://)?((?:www\.)?(?:postim(?:ages|g)|pixxxels)"
               r"\.(?:cc|org)/(?!gallery/)(?:image/)?([^/?#]+)/?)")
    example = "https://postimages.org/ID"

    def get_info(self, page):
        pos = page.index(' id="download"')
        url     , pos = text.rextract(page, ' href="', '"', pos)
        filename, pos = text.extract(page, 'class="imagename">', '<', pos)
        return url, text.unescape(filename)


class PostimgGalleryExtractor(ImagehostImageExtractor):
    """Extractor for images galleries from postimages.org"""
    category = "postimg"
    subcategory = "gallery"
    pattern = (r"(?:https?://)?((?:www\.)?(?:postim(?:ages|g)|pixxxels)"
               r"\.(?:cc|org)/gallery/([^/?#]+))")
    example = "https://postimages.org/gallery/ID"

    def items(self):
        page = self.request(self.page_url).text
        data = {"_extractor": PostimgImageExtractor}
        for url in text.extract_iter(page, ' class="thumb"><a href="', '"'):
            yield Message.Queue, url, data


class TurboimagehostImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from www.turboimagehost.com"""
    category = "turboimagehost"
    pattern = (r"(?:https?://)?((?:www\.)?turboimagehost\.com"
               r"/p/(\d+)/[^/?#]+\.html)")
    example = "https://www.turboimagehost.com/p/12345/NAME.EXT.html"

    def get_info(self, page):
        url = text.extract(page, 'src="', '"', page.index("<img "))[0]
        return url, url


class TurboimagehostGalleryExtractor(ImagehostImageExtractor):
    """Extractor for image galleries from turboimagehost.com"""
    category = "turboimagehost"
    subcategory = "gallery"
    pattern = (r"(?:https?://)?((?:www\.)?turboimagehost\.com"
               r"/album/(\d+)/([^/?#]*))")
    example = "https://www.turboimagehost.com/album/12345/GALLERY_NAME"

    def items(self):
        data = {"_extractor": TurboimagehostImageExtractor}
        params = {"p": 1}

        while True:
            page = self.request(self.page_url, params=params).text

            if params["p"] == 1 and \
                    "Requested gallery don`t exist on our website." in page:
                raise exception.NotFoundError("gallery")

            thumb_url = None
            for thumb_url in text.extract_iter(page, '"><a href="', '"'):
                yield Message.Queue, thumb_url, data
            if thumb_url is None:
                return

            params["p"] += 1


class ViprImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from vipr.im"""
    category = "vipr"
    pattern = r"(?:https?://)?(vipr\.im/(\w+))"
    example = "https://vipr.im/abc123.html"

    def get_info(self, page):
        url = text.extr(page, '<img src="', '"')
        return url, url


class ImgclickImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgclick.net"""
    category = "imgclick"
    pattern = r"(?:https?://)?((?:www\.)?imgclick\.net/([^/?#]+))"
    example = "http://imgclick.net/abc123/NAME.EXT.html"
    _https = False
    _params = "complex"

    def get_info(self, page):
        url     , pos = text.extract(page, '<br><img src="', '"')
        filename, pos = text.extract(page, 'alt="', '"', pos)
        return url, filename


class FappicImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from fappic.com"""
    category = "fappic"
    pattern = r"(?:https?://)?((?:www\.)?fappic\.com/(\w+)/[^/?#]+)"
    example = "https://fappic.com/abc123/NAME.EXT"

    def get_info(self, page):
        url     , pos = text.extract(page, '<a href="#"><img src="', '"')
        filename, pos = text.extract(page, 'alt="', '"', pos)

        if filename.startswith("Porn-Picture-"):
            filename = filename[13:]

        return url, filename
