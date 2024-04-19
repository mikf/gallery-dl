# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://e-hentai.org/ and https://exhentai.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import itertools
import math

BASE_PATTERN = r"(?:https?://)?(e[x-]|g\.e-)hentai\.org"


class ExhentaiExtractor(Extractor):
    """Base class for exhentai extractors"""
    category = "exhentai"
    directory_fmt = ("{category}", "{gid} {title[:247]}")
    filename_fmt = "{gid}_{num:>04}_{image_token}_{filename}.{extension}"
    archive_fmt = "{gid}_{num}"
    cookies_domain = ".exhentai.org"
    cookies_names = ("ipb_member_id", "ipb_pass_hash")
    root = "https://exhentai.org"
    request_interval = (3.0, 6.0)
    ciphers = "DEFAULT:!DH"

    LIMIT = False

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.version = match.group(1)

    def initialize(self):
        domain = self.config("domain", "auto")
        if domain == "auto":
            domain = ("ex" if self.version == "ex" else "e-") + "hentai.org"
        self.root = "https://" + domain
        self.api_url = self.root + "/api.php"
        self.cookies_domain = "." + domain

        Extractor.initialize(self)

        if self.version != "ex":
            self.cookies.set("nw", "1", domain=self.cookies_domain)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)
        if response.history and response.headers.get("Content-Length") == "0":
            self.log.info("blank page")
            raise exception.AuthorizationError()
        return response

    def login(self):
        """Login and set necessary cookies"""
        if self.LIMIT:
            raise exception.StopExtraction("Image limit reached!")

        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

        if self.version == "ex":
            self.log.info("No username or cookies given; using e-hentai.org")
            self.root = "https://e-hentai.org"
            self.cookies_domain = ".e-hentai.org"
            self.cookies.set("nw", "1", domain=self.cookies_domain)
        self.original = False
        self.limits = False

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "https://forums.e-hentai.org/index.php?act=Login&CODE=01"
        headers = {
            "Referer": "https://e-hentai.org/bounce_login.php?b=d&bt=1-1",
        }
        data = {
            "CookieDate": "1",
            "b": "d",
            "bt": "1-1",
            "UserName": username,
            "PassWord": password,
            "ipb_login_submit": "Login!",
        }

        self.cookies.clear()

        response = self.request(url, method="POST", headers=headers, data=data)
        content = response.content
        if b"You are now logged in as:" not in content:
            if b"The captcha was not entered correctly" in content:
                raise exception.AuthenticationError(
                    "CAPTCHA required. Use cookies instead.")
            raise exception.AuthenticationError()

        # collect more cookies
        url = self.root + "/favorites.php"
        response = self.request(url)
        if response.history:
            self.request(url)

        return self.cookies


class ExhentaiGalleryExtractor(ExhentaiExtractor):
    """Extractor for image galleries from exhentai.org"""
    subcategory = "gallery"
    pattern = (BASE_PATTERN +
               r"(?:/g/(\d+)/([\da-f]{10})"
               r"|/s/([\da-f]{10})/(\d+)-(\d+))")
    example = "https://e-hentai.org/g/12345/67890abcde/"

    def __init__(self, match):
        ExhentaiExtractor.__init__(self, match)
        self.gallery_id = text.parse_int(match.group(2) or match.group(5))
        self.gallery_token = match.group(3)
        self.image_token = match.group(4)
        self.image_num = text.parse_int(match.group(6), 1)
        self.key_start = None
        self.key_show = None
        self.key_next = None
        self.count = 0
        self.data = None

    def _init(self):
        source = self.config("source")
        if source == "hitomi":
            self.items = self._items_hitomi

        limits = self.config("limits", False)
        if limits and limits.__class__ is int:
            self.limits = limits
            self._remaining = 0
        else:
            self.limits = False

        self.fallback_retries = self.config("fallback-retries", 2)
        self.original = self.config("original", True)

    def finalize(self):
        if self.data:
            self.log.info("Use '%s/s/%s/%s-%s' as input URL "
                          "to continue downloading from the current position",
                          self.root, self.data["image_token"],
                          self.gallery_id, self.data["num"])

    def favorite(self, slot="0"):
        url = self.root + "/gallerypopups.php"
        params = {
            "gid": self.gallery_id,
            "t"  : self.gallery_token,
            "act": "addfav",
        }
        data = {
            "favcat" : slot,
            "apply"  : "Apply Changes",
            "update" : "1",
        }
        self.request(url, method="POST", params=params, data=data)

    def items(self):
        self.login()

        if self.gallery_token:
            gpage = self._gallery_page()
            self.image_token = text.extr(gpage, 'hentai.org/s/', '"')
            if not self.image_token:
                self.log.debug("Page content:\n%s", gpage)
                raise exception.StopExtraction(
                    "Failed to extract initial image token")
            ipage = self._image_page()
        else:
            ipage = self._image_page()
            part = text.extr(ipage, 'hentai.org/g/', '"')
            if not part:
                self.log.debug("Page content:\n%s", ipage)
                raise exception.StopExtraction(
                    "Failed to extract gallery token")
            self.gallery_token = part.split("/")[1]
            gpage = self._gallery_page()

        self.data = data = self.get_metadata(gpage)
        self.count = text.parse_int(data["filecount"])
        yield Message.Directory, data

        images = itertools.chain(
            (self.image_from_page(ipage),), self.images_from_api())
        for url, image in images:
            data.update(image)
            if self.limits:
                self._check_limits(data)
            if "/fullimg" in url:
                data["_http_validate"] = self._validate_response
            else:
                data["_http_validate"] = None
            yield Message.Url, url, data

        fav = self.config("fav")
        if fav is not None:
            self.favorite(fav)
        self.data = None

    def _items_hitomi(self):
        if self.config("metadata", False):
            data = self.metadata_from_api()
            data["date"] = text.parse_timestamp(data["posted"])
        else:
            data = {}

        from .hitomi import HitomiGalleryExtractor
        url = "https://hitomi.la/galleries/{}.html".format(self.gallery_id)
        data["_extractor"] = HitomiGalleryExtractor
        yield Message.Queue, url, data

    def get_metadata(self, page):
        """Extract gallery metadata"""
        data = self.metadata_from_page(page)
        if self.config("metadata", False):
            data.update(self.metadata_from_api())
            data["date"] = text.parse_timestamp(data["posted"])
        return data

    def metadata_from_page(self, page):
        extr = text.extract_from(page)

        api_url = extr('var api_url = "', '"')
        if api_url:
            self.api_url = api_url

        data = {
            "gid"          : self.gallery_id,
            "token"        : self.gallery_token,
            "thumb"        : extr("background:transparent url(", ")"),
            "title"        : text.unescape(extr('<h1 id="gn">', '</h1>')),
            "title_jpn"    : text.unescape(extr('<h1 id="gj">', '</h1>')),
            "_"            : extr('<div id="gdc"><div class="cs ct', '"'),
            "eh_category"  : extr('>', '<'),
            "uploader"     : extr('<div id="gdn">', '</div>'),
            "date"         : text.parse_datetime(extr(
                '>Posted:</td><td class="gdt2">', '</td>'), "%Y-%m-%d %H:%M"),
            "parent"       : extr(
                '>Parent:</td><td class="gdt2"><a href="', '"'),
            "expunged"     : "Yes" != extr(
                '>Visible:</td><td class="gdt2">', '<'),
            "language"     : extr('>Language:</td><td class="gdt2">', ' '),
            "filesize"     : text.parse_bytes(extr(
                '>File Size:</td><td class="gdt2">', '<').rstrip("Bbi")),
            "filecount"    : extr('>Length:</td><td class="gdt2">', ' '),
            "favorites"    : extr('id="favcount">', ' '),
            "rating"       : extr(">Average: ", "<"),
            "torrentcount" : extr('>Torrent Download (', ')'),
        }

        if data["uploader"].startswith("<"):
            data["uploader"] = text.unescape(text.extr(
                data["uploader"], ">", "<"))

        f = data["favorites"][0]
        if f == "N":
            data["favorites"] = "0"
        elif f == "O":
            data["favorites"] = "1"

        data["lang"] = util.language_to_code(data["language"])
        data["tags"] = [
            text.unquote(tag.replace("+", " "))
            for tag in text.extract_iter(page, 'hentai.org/tag/', '"')
        ]

        return data

    def metadata_from_api(self):
        data = {
            "method"   : "gdata",
            "gidlist"  : ((self.gallery_id, self.gallery_token),),
            "namespace": 1,
        }

        data = self.request(self.api_url, method="POST", json=data).json()
        if "error" in data:
            raise exception.StopExtraction(data["error"])

        return data["gmetadata"][0]

    def image_from_page(self, page):
        """Get image url and data from webpage"""
        pos = page.index('<div id="i3"><a onclick="return load_image(') + 26
        extr = text.extract_from(page, pos)

        self.key_next = extr("'", "'")
        iurl = extr('<img id="img" src="', '"')
        nl = extr(" nl(", ")").strip("\"'")
        orig = extr('hentai.org/fullimg', '"')

        try:
            if self.original and orig:
                url = self.root + "/fullimg" + text.unescape(orig)
                data = self._parse_original_info(extr('ownload original', '<'))
                data["_fallback"] = self._fallback_original(nl, url)
            else:
                url = iurl
                data = self._parse_image_info(url)
                data["_fallback"] = self._fallback_1280(nl, self.image_num)
        except IndexError:
            self.log.debug("Page content:\n%s", page)
            raise exception.StopExtraction(
                "Unable to parse image info for '%s'", url)

        data["num"] = self.image_num
        data["image_token"] = self.key_start = extr('var startkey="', '";')
        data["_url_1280"] = iurl
        data["_nl"] = nl
        self.key_show = extr('var showkey="', '";')

        self._check_509(iurl)
        return url, text.nameext_from_url(url, data)

    def images_from_api(self):
        """Get image url and data from api calls"""
        api_url = self.api_url
        nextkey = self.key_next
        request = {
            "method" : "showpage",
            "gid"    : self.gallery_id,
            "page"   : 0,
            "imgkey" : nextkey,
            "showkey": self.key_show,
        }

        for request["page"] in range(self.image_num + 1, self.count + 1):
            page = self.request(api_url, method="POST", json=request).json()

            i3 = page["i3"]
            i6 = page["i6"]

            imgkey = nextkey
            nextkey, pos = text.extract(i3, "'", "'")
            imgurl , pos = text.extract(i3, 'id="img" src="', '"', pos)
            nl     , pos = text.extract(i3, " nl(", ")", pos)
            nl = (nl or "").strip("\"'")

            try:
                pos = i6.find("hentai.org/fullimg")
                if self.original and pos >= 0:
                    origurl, pos = text.rextract(i6, '"', '"', pos)
                    url = text.unescape(origurl)
                    data = self._parse_original_info(text.extract(
                        i6, "ownload original", "<", pos)[0])
                    data["_fallback"] = self._fallback_original(nl, url)
                else:
                    url = imgurl
                    data = self._parse_image_info(url)
                    data["_fallback"] = self._fallback_1280(
                        nl, request["page"], imgkey)
            except IndexError:
                self.log.debug("Page content:\n%s", page)
                raise exception.StopExtraction(
                    "Unable to parse image info for '%s'", url)

            data["num"] = request["page"]
            data["image_token"] = imgkey
            data["_url_1280"] = imgurl
            data["_nl"] = nl

            self._check_509(imgurl)
            yield url, text.nameext_from_url(url, data)

            request["imgkey"] = nextkey

    def _validate_response(self, response):
        if not response.history and response.headers.get(
                "content-type", "").startswith("text/html"):
            page = response.text
            self.log.warning("'%s'", page)

            if " requires GP" in page:
                gp = self.config("gp")
                if gp == "stop":
                    raise exception.StopExtraction("Not enough GP")
                elif gp == "wait":
                    input("Press ENTER to continue.")
                    return response.url

                self.log.info("Falling back to non-original downloads")
                self.original = False
                return self.data["_url_1280"]

            self._report_limits()
        return True

    def _report_limits(self):
        ExhentaiExtractor.LIMIT = True
        raise exception.StopExtraction("Image limit reached!")

    def _check_limits(self, data):
        if not self._remaining or data["num"] % 25 == 0:
            self._update_limits()
        self._remaining -= data["cost"]
        if self._remaining <= 0:
            self._report_limits()

    def _check_509(self, url):
        # full 509.gif URLs
        # - https://exhentai.org/img/509.gif
        # - https://ehgt.org/g/509.gif
        if url.endswith(("hentai.org/img/509.gif",
                         "ehgt.org/g/509.gif")):
            self.log.debug(url)
            self._report_limits()

    def _update_limits(self):
        url = "https://e-hentai.org/home.php"
        cookies = {
            cookie.name: cookie.value
            for cookie in self.cookies
            if cookie.domain == self.cookies_domain and
            cookie.name != "igneous"
        }

        page = self.request(url, cookies=cookies).text
        current = text.extr(page, "<strong>", "</strong>")
        self.log.debug("Image Limits: %s/%s", current, self.limits)
        self._remaining = self.limits - text.parse_int(current)

    def _gallery_page(self):
        url = "{}/g/{}/{}/".format(
            self.root, self.gallery_id, self.gallery_token)
        response = self.request(url, fatal=False)
        page = response.text

        if response.status_code == 404 and "Gallery Not Available" in page:
            raise exception.AuthorizationError()
        if page.startswith(("Key missing", "Gallery not found")):
            raise exception.NotFoundError("gallery")
        if "hentai.org/mpv/" in page:
            self.log.warning("Enabled Multi-Page Viewer is not supported")
        return page

    def _image_page(self):
        url = "{}/s/{}/{}-{}".format(
            self.root, self.image_token, self.gallery_id, self.image_num)
        page = self.request(url, fatal=False).text

        if page.startswith(("Invalid page", "Keep trying")):
            raise exception.NotFoundError("image page")
        return page

    def _fallback_original(self, nl, fullimg):
        url = "{}?nl={}".format(fullimg, nl)
        for _ in util.repeat(self.fallback_retries):
            yield url

    def _fallback_1280(self, nl, num, token=None):
        if not token:
            token = self.key_start

        for _ in util.repeat(self.fallback_retries):
            url = "{}/s/{}/{}-{}?nl={}".format(
                self.root, token, self.gallery_id, num, nl)

            page = self.request(url, fatal=False).text
            if page.startswith(("Invalid page", "Keep trying")):
                return
            url, data = self.image_from_page(page)
            yield url

            nl = data["_nl"]

    @staticmethod
    def _parse_image_info(url):
        for part in url.split("/")[4:]:
            try:
                _, size, width, height, _ = part.split("-")
                break
            except ValueError:
                pass
        else:
            size = width = height = 0

        return {
            "cost"  : 1,
            "size"  : text.parse_int(size),
            "width" : text.parse_int(width),
            "height": text.parse_int(height),
        }

    @staticmethod
    def _parse_original_info(info):
        parts = info.lstrip().split(" ")
        size = text.parse_bytes(parts[3] + parts[4][0])

        return {
            # 1 initial point + 1 per 0.1 MB
            "cost"  : 1 + math.ceil(size / 100000),
            "size"  : size,
            "width" : text.parse_int(parts[0]),
            "height": text.parse_int(parts[2]),
        }


class ExhentaiSearchExtractor(ExhentaiExtractor):
    """Extractor for exhentai search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:\?([^#]*)|tag/([^/?#]+))"
    example = "https://e-hentai.org/?f_search=QUERY"

    def __init__(self, match):
        ExhentaiExtractor.__init__(self, match)

        _, query, tag = match.groups()
        if tag:
            if "+" in tag:
                ns, _, tag = tag.rpartition(":")
                tag = '{}:"{}$"'.format(ns, tag.replace("+", " "))
            else:
                tag += "$"
            self.params = {"f_search": tag, "page": 0}
        else:
            self.params = text.parse_query(query)
            if "next" not in self.params:
                self.params["page"] = text.parse_int(self.params.get("page"))

    def _init(self):
        self.search_url = self.root

    def items(self):
        self.login()
        data = {"_extractor": ExhentaiGalleryExtractor}
        search_url = self.search_url
        params = self.params

        while True:
            last = None
            page = self.request(search_url, params=params).text

            for gallery in ExhentaiGalleryExtractor.pattern.finditer(page):
                url = gallery.group(0)
                if url == last:
                    continue
                last = url
                data["gallery_id"] = text.parse_int(gallery.group(2))
                data["gallery_token"] = gallery.group(3)
                yield Message.Queue, url + "/", data

            next_url = text.extr(page, 'nexturl="', '"', None)
            if next_url is not None:
                if not next_url:
                    return
                search_url = next_url
                params = None

            elif 'class="ptdd">&gt;<' in page or ">No hits found</p>" in page:
                return
            else:
                params["page"] += 1


class ExhentaiFavoriteExtractor(ExhentaiSearchExtractor):
    """Extractor for favorited exhentai galleries"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/favorites\.php(?:\?([^#]*)())?"
    example = "https://e-hentai.org/favorites.php"

    def _init(self):
        self.search_url = self.root + "/favorites.php"
