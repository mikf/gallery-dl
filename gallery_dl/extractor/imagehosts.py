# -*- coding: utf-8 -*-

# Copyright 2016-2025 Mike Fährmann
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
    parent = True
    _https = True
    _params = None
    _cookies = None
    _encoding = None
    _validate = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        if self.root:
            self.page_url = f"{self.root}{match[1]}"
        else:
            self.page_url = f"http{'s' if self._https else ''}://{match[1]}"
        self.token = match[2]

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
        if not url:
            return

        if filename:
            data = text.nameext_from_name(filename)
            if not data["extension"]:
                data["extension"] = text.ext_from_url(url)
        else:
            data = text.nameext_from_url(url)
        data["token"] = self.token
        data["post_url"] = self.page_url
        data.update(self.metadata(page))

        if self._https and url.startswith("http:"):
            url = "https:" + url[5:]
        if self._validate is not None:
            data["_http_validate"] = self._validate

        yield Message.Directory, "", data
        yield Message.Url, url, data

    def get_info(self, page):
        """Find image-url and string to get filename from"""

    def metadata(self, page):
        """Return additional metadata"""
        return ()

    def not_found(self, resource=None):
        raise exception.NotFoundError(resource or self.__class__.subcategory)


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
            self.not_found()
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

        params = {"page": 1}
        while True:
            for url in text.extract_iter(page, "<a href=", " ", pos):
                if "/i/" in url:
                    yield Message.Queue, url.strip("\"'"), data

            if 'class="pagination' not in page or \
                    'class="disabled">Last' in page:
                return

            params["page"] += 1
            page = self.request(self.page_url, params=params).text


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
                self.not_found()

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
        try:
            pos = page.index('class="card-body')
        except ValueError:
            self.not_found()

        url, pos = text.extract(page, '<img src="', '"', pos)
        if url.endswith("/loader.svg"):
            url, pos = text.extract(page, '<img src="', '"', pos)
        filename, pos = text.extract(page, 'alt="', '"', pos)
        return url, text.unescape(filename)

    def _validate(self, response):
        hget = response.headers.get
        return not (
            hget("content-length") == "14396" and
            hget("content-type") == "image/jpeg" and
            hget("last-modified") == "Mon, 04 May 2020 07:19:52 GMT"
        )


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
        if url and url.startswith("/imgs/"):
            self.not_found()
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


class ImgadultImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgadult.com"""
    category = "imgadult"
    _cookies = {"img_i_d": "1"}
    pattern = r"(?:https?://)?((?:www\.)?imgadult\.com/img-([0-9a-f]+)\.html)"
    example = "https://imgadult.com/img-0123456789abc.html"

    def get_info(self, page):
        url , pos = text.extract(page, "' src='", "'")
        name, pos = text.extract(page, "alt='", "'", pos)

        if name:
            name, _, rhs = name.rpartition(" image hosted at ImgAdult.com")
            if not name:
                name = rhs
            name = text.unescape(name)

        return url, name


class ImgspiceImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgspice.com"""
    category = "imgspice"
    pattern = r"(?:https?://)?((?:www\.)?imgspice\.com/([^/?#]+))"
    example = "https://imgspice.com/ID/NAME.EXT.html"

    def get_info(self, page):
        pos = page.find('id="imgpreview"')
        if pos < 0:
            self.not_found()
        url , pos = text.extract(page, 'src="', '"', pos)
        name, pos = text.extract(page, 'alt="', '"', pos)
        return url, text.unescape(name)


class PixhostImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from pixhost.to"""
    category = "pixhost"
    root = "https://pixhost.to"
    pattern = (r"(?:https?://)?(?:www\.)?pixhost\.(?:to|org)"
               r"(/show/\d+/(\d+)_[^/?#]+)")
    example = "https://pixhost.to/show/123/12345_NAME.EXT"
    _cookies = {"pixhostads": "1", "pixhosttest": "1"}

    def get_info(self, page):
        self.kwdict["directory"] = self.page_url.rsplit("/")[-2]
        url , pos = text.extract(page, "class=\"image-img\" src=\"", "\"")
        name, pos = text.extract(page, "alt=\"", "\"", pos)
        return url, text.unescape(name) if name else None


class PixhostGalleryExtractor(ImagehostImageExtractor):
    """Extractor for image galleries from pixhost.to"""
    category = "pixhost"
    subcategory = "gallery"
    root = "https://pixhost.to"
    pattern = (r"(?:https?://)?(?:www\.)?pixhost\.(?:to|org)"
               r"(/gallery/([^/?#]+))")
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
    root = "https://postimg.cc"
    pattern = (r"(?:https?://)?(?:www\.)?(?:postim(?:ages|g)|pixxxels)"
               r"\.(?:cc|org)(/(?!gallery/)(?:image/)?([^/?#]+)/?)")
    example = "https://postimg.cc/ID"

    def get_info(self, page):
        pos = page.index(' id="download"')
        url     , pos = text.rextract(page, ' href="', '"', pos)
        filename, pos = text.extract(page, ' class="my-4">', '<', pos)
        return url, text.unescape(filename) if filename else None


class PostimgGalleryExtractor(ImagehostImageExtractor):
    """Extractor for images galleries from postimages.org"""
    category = "postimg"
    subcategory = "gallery"
    root = "https://postimg.cc"
    pattern = (r"(?:https?://)?(?:www\.)?(?:postim(?:ages|g)|pixxxels)"
               r"\.(?:cc|org)(/gallery/([^/?#]+))")
    example = "https://postimg.cc/gallery/ID"

    def items(self):
        page = self.request(self.page_url).text
        title = text.extr(
            page, 'property="og:title" content="', ' — Postimages"')

        data = {
            "_extractor"   : PostimgImageExtractor,
            "gallery_title": text.unescape(title),
        }

        for token in text.extract_iter(page, 'data-image="', '"'):
            url = f"{self.root}/{token}"
            yield Message.Queue, url, data


class TurboimagehostImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from www.turboimagehost.com"""
    category = "turboimagehost"
    pattern = (r"(?:https?://)?((?:www\.)?turboimagehost\.com"
               r"/p/(\d+)/[^/?#]+\.html)")
    example = "https://www.turboimagehost.com/p/12345/NAME.EXT.html"

    def get_info(self, page):
        url = text.extract(page, 'src="', '"', page.index("<img "))[0]
        return url, None


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
                self.not_found()

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
        return url, None


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
    pattern = (r"(?:https?://)?(?:www\.|img\d+\.)?fappic\.com"
               r"/(?:i/\d+/())?(\w{10,})(?:/|\.)\w+")
    example = "https://fappic.com/abcde12345/NAME.EXT"

    def __init__(self, match):
        Extractor.__init__(self, match)

        thumb, token = self.groups
        if thumb is not None and token.endswith("_t"):
            self.token = token = token[:-2]
        else:
            self.token = token
        self.page_url = f"https://fappic.com/{token}/pic.jpg"

    def get_info(self, page):
        url     , pos = text.extract(page, '<a href="#"><img src="', '"')
        filename, pos = text.extract(page, 'alt="', '"', pos)
        return url, text.re(r"^Porn[ -]Pic(?:s|ture)[ -]").sub("", filename)


class PicstateImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from picstate.com"""
    category = "picstate"
    pattern = r"(?:https?://)?((?:www\.)?picstate\.com/view/full/([^/?#]+))"
    example = "https://picstate.com/view/full/123"

    def get_info(self, page):
        pos = page.index(' id="image_container"')
        url     , pos = text.extract(page, '<img src="', '"', pos)
        filename, pos = text.extract(page, 'alt="', '"', pos)
        return url, filename


class ImgdriveImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from imgdrive.net"""
    category = "imgdrive"
    pattern = (r"(?:https?://)?(?:www\.)?(img(drive|taxi|wallet)\.(?:com|net)"
               r"/img-(\w+)\.html)")
    example = "https://imgdrive.net/img-0123456789abc.html"

    def __init__(self, match):
        path, category, self.token = match.groups()
        self.page_url = f"https://{path}"
        self.category = f"img{category}"
        Extractor.__init__(self, match)

    def get_info(self, page):
        title, pos = text.extract(
            page, 'property="og:title" content="', '"')
        image, pos = text.extract(
            page, 'property="og:image" content="', '"', pos)
        return image.replace("/small/", "/big/"), title.rsplit(" | ", 2)[0]


class SilverpicImageExtractor(ImagehostImageExtractor):
    """Extractor for single images from silverpic.com"""
    category = "silverpic"
    root = "https://silverpic.net"
    _params = "complex"
    pattern = (r"(?:https?://)?(?:www\.)?silverpic\.(?:net|com)"
               r"(/([a-z0-9]{10,})/[\S]+\.html)")
    example = "https://silverpic.net/a1b2c3d4f5g6/NAME.EXT.html"

    def get_info(self, page):
        url, pos = text.extract(page, '<img src="/img/', '"')
        alt, pos = text.extract(page, 'alt="', '"', pos)
        return f"{self.root}/img/{url}", alt

    def metadata(self, page):
        pos = page.find('<img src="/img/')
        width = text.extract(page, 'width="', '"', pos)[0]
        height = text.extract(page, 'height="', '"', pos)[0]

        return {
            "width" : text.parse_int(width),
            "height": text.parse_int(height),
        }
