# -*- coding: utf-8 -*-

# Copyright 2014-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at https://exhentai.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import itertools
import random
import time
import math


BASE_PATTERN = r"(?:https?://)?(e[x-]|g\.e-)hentai\.org"


class ExhentaiExtractor(Extractor):
    """Base class for exhentai extractors"""
    category = "exhentai"
    directory_fmt = ("{category}", "{gallery_id}")
    filename_fmt = (
        "{gallery_id}_{num:>04}_{image_token}_{filename}.{extension}")
    archive_fmt = "{gallery_id}_{num}"
    cookiedomain = ".exhentai.org"
    cookienames = ("ipb_member_id", "ipb_pass_hash")
    root = "https://exhentai.org"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.limits = self.config("limits", True)
        self.original = self.config("original", True)
        self.wait_min = self.config("wait-min", 3)
        self.wait_max = self.config("wait-max", 6)

        self._remaining = 0
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min
        self.session.headers["Referer"] = self.root + "/"

    def request(self, *args, **kwargs):
        response = Extractor.request(self, *args, **kwargs)
        if self._is_sadpanda(response):
            self.log.info("sadpanda.jpg")
            raise exception.AuthorizationError()
        return response

    def wait(self, waittime=None):
        """Wait for a randomly chosen amount of seconds"""
        if not waittime:
            waittime = random.uniform(self.wait_min, self.wait_max)
        else:
            waittime = random.uniform(waittime * 0.66, waittime * 1.33)
        time.sleep(waittime)

    def login(self):
        """Login and set necessary cookies"""
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))
        else:
            self.log.info("no username given; using e-hentai.org")
            self.root = "https://e-hentai.org"
            self.original = False
            self.limits = False
            self.session.cookies["nw"] = "1"

    @cache(maxage=90*24*3600, keyarg=1)
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

        response = self.request(url, method="POST", headers=headers, data=data)
        if "You are now logged in as:" not in response.text:
            raise exception.AuthenticationError()
        return {c: response.cookies[c] for c in self.cookienames}

    @staticmethod
    def _is_sadpanda(response):
        """Return True if the response object contains a sad panda"""
        return (
            response.headers.get("Content-Length") == "9615" and
            "sadpanda.jpg" in response.headers.get("Content-Disposition", "")
        )


class ExhentaiGalleryExtractor(ExhentaiExtractor):
    """Extractor for image galleries from exhentai.org"""
    subcategory = "gallery"
    pattern = (BASE_PATTERN +
               r"(?:/g/(\d+)/([\da-f]{10})"
               r"|/s/([\da-f]{10})/(\d+)-(\d+))")
    test = (
        ("https://exhentai.org/g/960460/4f0e369d82/", {
            "keyword": "1532ca4d0e4e0738dc994ca725a228af04a4e480",
            "content": "493d759de534355c9f55f8e365565b62411de146",
        }),
        ("https://exhentai.org/g/960461/4f0e369d82/", {
            "exception": exception.NotFoundError,
        }),
        ("http://exhentai.org/g/962698/7f02358e00/", {
            "exception": exception.AuthorizationError,
        }),
        ("https://exhentai.org/s/3957343c3b/960460-5", {
            "count": 2,
        }),
        ("https://e-hentai.org/g/960460/4f0e369d82/"),
        ("https://g.e-hentai.org/g/960460/4f0e369d82/"),
    )

    def __init__(self, match):
        ExhentaiExtractor.__init__(self, match)
        self.key = {}
        self.count = 0
        self.gallery_id = text.parse_int(match.group(2) or match.group(5))
        self.gallery_token = match.group(3)
        self.image_token = match.group(4)
        self.image_num = text.parse_int(match.group(6), 1)

    def items(self):
        self.login()

        if self.gallery_token:
            gpage = self._gallery_page()
            self.image_token = text.extract(gpage, 'hentai.org/s/', '"')[0]
            self.wait()
            ipage = self._image_page()
        else:
            ipage = self._image_page()
            part = text.extract(ipage, 'hentai.org/g/', '"')[0]
            self.gallery_token = part.split("/")[1]
            self.wait()
            gpage = self._gallery_page()

        data = self.get_metadata(gpage)
        self.count = data["count"]

        yield Message.Version, 1
        yield Message.Directory, data

        images = itertools.chain(
            (self.image_from_page(ipage),), self.images_from_api())
        for url, image in images:
            data.update(image)
            if self.limits:
                self._check_limits(data)
            if "/fullimg.php" in url:
                data["extension"] = ""
                self.wait(1.5)
            yield Message.Url, url, data

    def get_metadata(self, page):
        """Extract gallery metadata"""
        extr = text.extract_from(page)
        data = {
            "gallery_id"   : self.gallery_id,
            "gallery_token": self.gallery_token,
            "title"        : text.unescape(extr('<h1 id="gn">', '</h1>')),
            "title_jp"     : text.unescape(extr('<h1 id="gj">', '</h1>')),
            "date"         : text.parse_datetime(extr(
                '>Posted:</td><td class="gdt2">', '</td>'), "%Y-%m-%d %H:%M"),
            "parent"       : extr(
                '>Parent:</td><td class="gdt2"><a href="', '"'),
            "visible"      : extr(
                '>Visible:</td><td class="gdt2">', '<'),
            "language"     : extr(
                '>Language:</td><td class="gdt2">', ' '),
            "gallery_size" : text.parse_bytes(extr(
                '>File Size:</td><td class="gdt2">', '<').rstrip("Bb")),
            "count"        : text.parse_int(extr(
                '>Length:</td><td class="gdt2">', ' ')),
        }

        data["lang"] = util.language_to_code(data["language"])
        data["tags"] = [
            text.unquote(tag)
            for tag in text.extract_iter(page, 'hentai.org/tag/', '"')
        ]

        return data

    def image_from_page(self, page):
        """Get image url and data from webpage"""
        pos = page.index('<div id="i3"><a onclick="return load_image(') + 26
        extr = text.extract_from(page, pos)

        self.key["next"] = extr("'", "'")
        iurl = extr('<img id="img" src="', '"')
        orig = extr('hentai.org/fullimg.php', '"')

        if self.original and orig:
            url = self.root + "/fullimg.php" + text.unescape(orig)
            data = self._parse_original_info(extr('ownload original', '<'))
        else:
            url = iurl
            data = self._parse_image_info(url)

        data["num"] = self.image_num
        data["image_token"] = self.key["start"] = extr('var startkey="', '";')
        self.key["show"] = extr('var showkey="', '";')

        return url, text.nameext_from_url(iurl, data)

    def images_from_api(self):
        """Get image url and data from api calls"""
        api_url = self.root + "/api.php"
        nextkey = self.key["next"]
        request = {
            "method" : "showpage",
            "gid"    : self.gallery_id,
            "imgkey" : nextkey,
            "showkey": self.key["show"],
        }
        for request["page"] in range(self.image_num + 1, self.count + 1):
            self.wait()
            page = self.request(api_url, method="POST", json=request).json()
            imgkey = nextkey
            nextkey, pos = text.extract(page["i3"], "'", "'")
            imgurl , pos = text.extract(page["i3"], 'id="img" src="', '"', pos)
            origurl, pos = text.extract(page["i7"], '<a href="', '"')

            if self.original and origurl:
                url = text.unescape(origurl)
                data = self._parse_original_info(
                    text.extract(page["i7"], "ownload original", "<", pos)[0])
            else:
                url = imgurl
                data = self._parse_image_info(url)

            data["num"] = request["page"]
            data["image_token"] = imgkey
            yield url, text.nameext_from_url(imgurl, data)

            request["imgkey"] = nextkey

    def _gallery_page(self):
        url = "{}/g/{}/{}/".format(
            self.root, self.gallery_id, self.gallery_token)
        response = self.request(url, expect=range(400, 500))
        page = response.text

        if response.status_code == 404 and "Gallery Not Available" in page:
            raise exception.AuthorizationError()
        if page.startswith(("Key missing", "Gallery not found")):
            raise exception.NotFoundError("gallery")
        return page

    def _image_page(self):
        url = "{}/s/{}/{}-{}".format(
            self.root, self.image_token, self.gallery_id, self.image_num)
        page = self.request(url, expect=range(400, 500)).text

        if page.startswith(("Invalid page", "Keep trying")):
            raise exception.NotFoundError("image page")
        return page

    def _check_limits(self, data):
        if not self._remaining or data["num"] % 20 == 0:
            self._update_limits()
        self._remaining -= data["cost"]

        if self._remaining <= 0:
            url = "{}/s/{}/{}-{}".format(
                self.root, data["image_token"], self.gallery_id, data["num"])
            self.log.error(
                "Image limit reached! Reset it and continue with "
                "'%s' as URL.", url)
            raise exception.StopExtraction()

    def _update_limits(self):
        url = "https://e-hentai.org/home.php"
        cookies = {
            cookie.name: cookie.value
            for cookie in self.session.cookies
            if cookie.domain == self.cookiedomain and cookie.name != "igneous"
        }

        page = self.request(url, cookies=cookies).text
        current, pos = text.extract(page, "<strong>", "</strong>")
        maximum, pos = text.extract(page, "<strong>", "</strong>", pos)
        self._remaining = text.parse_int(maximum) - text.parse_int(current)

    @staticmethod
    def _parse_image_info(url):
        parts = url.split("/")[4].split("-")
        return {
            "width": text.parse_int(parts[2]),
            "height": text.parse_int(parts[3]),
            "size": text.parse_int(parts[1]),
            "cost": 1,
        }

    @staticmethod
    def _parse_original_info(info):
        parts = info.lstrip().split(" ")
        size = text.parse_bytes(parts[3] + parts[4][0])
        return {
            "width": text.parse_int(parts[0]),
            "height": text.parse_int(parts[2]),
            "size": size,
            "cost": 1 + math.ceil(size * 5 / 1024 / 1024)
        }


class ExhentaiSearchExtractor(ExhentaiExtractor):
    """Extractor for exhentai search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/?\?(.*)$"
    test = (
        ("https://exhentai.org/?f_search=touhou"),
        (("https://exhentai.org/?f_doujinshi=0&f_manga=0&f_artistcg=0"
          "&f_gamecg=0&f_western=0&f_non-h=1&f_imageset=0&f_cosplay=0"
          "&f_asianporn=0&f_misc=0&f_search=touhou&f_apply=Apply+Filter"), {
            "pattern": ExhentaiGalleryExtractor.pattern,
            "range": "1-30",
            "count": 30,
        }),
    )

    def __init__(self, match):
        ExhentaiExtractor.__init__(self, match)
        self.params = text.parse_query(match.group(2))
        self.params["page"] = text.parse_int(self.params.get("page"))
        self.search_url = self.root

    def items(self):
        self.login()
        yield Message.Version, 1

        while True:
            last = None
            page = self.request(self.search_url, params=self.params).text

            for gallery in ExhentaiGalleryExtractor.pattern.finditer(page):
                url = gallery.group(0)
                if url == last:
                    continue
                last = url
                yield Message.Queue, url, {}

            if 'class="ptdd">&gt;<' in page or ">No hits found</p>" in page:
                return
            self.params["page"] += 1
            self.wait()


class ExhentaiFavoriteExtractor(ExhentaiSearchExtractor):
    """Extractor for favorited exhentai galleries"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/favorites\.php(?:\?(.*))?"
    test = (
        ("https://exhentai.org/favorites.php"),
        ("https://exhentai.org/favorites.php?favcat=1&f_search=touhou"
         "&f_apply=Search+Favorites"),
    )

    def __init__(self, match):
        ExhentaiSearchExtractor.__init__(self, match)
        self.search_url = self.root + "/favorites.php"
