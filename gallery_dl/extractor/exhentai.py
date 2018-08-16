# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at https://exhentai.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import time
import random


class ExhentaiExtractor(Extractor):
    """Base class for exhentai extractors"""
    category = "exhentai"
    directory_fmt = ["{category}", "{gallery_id}"]
    filename_fmt = "{gallery_id}_{num:>04}_{image_token}_{name}.{extension}"
    archive_fmt = "{gallery_id}_{num}"
    cookiedomain = ".exhentai.org"
    cookienames = ("ipb_member_id", "ipb_pass_hash")
    root = "https://exhentai.org"

    def __init__(self):
        Extractor.__init__(self)
        self.original = self.config("original", True)
        self.wait_min = self.config("wait-min", 3)
        self.wait_max = self.config("wait-max", 6)
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
        if not username:
            self.log.info("no username given; using e-hentai.org")
            self.root = "https://e-hentai.org"
            self.original = False
            self.session.cookies["nw"] = "1"
            return
        cookies = self._login_impl(username, password)
        for key, value in cookies.items():
            self.session.cookies.set(
                key, value, domain=self.cookiedomain)

    @cache(maxage=90*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        self.log.info("Logging in as %s", username)
        url = "https://forums.e-hentai.org/index.php?act=Login&CODE=01"
        data = {
            "CookieDate": "1",
            "b": "d",
            "bt": "1-1",
            "UserName": username,
            "PassWord": password,
            "ipb_login_submit": "Login!",
        }
        headers = {
            "Referer": "https://e-hentai.org/bounce_login.php?b=d&bt=1-1"
        }
        response = self.request(url, method="POST", data=data, headers=headers)

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
    pattern = [r"(?:https?://)?(g\.e-|e-|ex)hentai\.org/g/(\d+)/([\da-f]{10})"]
    test = [
        ("https://exhentai.org/g/960460/4f0e369d82/", {
            "keyword": "15b755fd3e2c710d7fd7ff112a5cdbf4333201b2",
            "content": "493d759de534355c9f55f8e365565b62411de146",
        }),
        ("https://exhentai.org/g/960461/4f0e369d82/", {
            "exception": exception.NotFoundError,
        }),
        ("http://exhentai.org/g/962698/7f02358e00/", {
            "exception": exception.AuthorizationError,
        }),
        ("https://e-hentai.org/g/960460/4f0e369d82/", None),
        ("https://g.e-hentai.org/g/960460/4f0e369d82/", None),
    ]

    def __init__(self, match):
        ExhentaiExtractor.__init__(self)
        self.key = {}
        self.count = 0
        self.version, self.gid, self.token = match.groups()
        self.gid = text.parse_int(self.gid)

    def items(self):
        self.login()
        yield Message.Version, 1

        url = "{}/g/{}/{}/".format(self.root, self.gid, self.token)
        response = self.request(url, expect=range(400, 500))
        page = response.text

        if response.status_code == 404 and "Gallery Not Available" in page:
            raise exception.AuthorizationError()
        if page.startswith(("Key missing", "Gallery not found")):
            raise exception.NotFoundError("gallery")

        data = self.get_job_metadata(page)
        self.count = data["count"]
        yield Message.Directory, data

        for url, image in self.get_images(page):
            data.update(image)
            if "/fullimg.php" in url:
                data["extension"] = ""
                self.wait(1.5)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "gallery_id"   : self.gid,
            "gallery_token": self.token,
        }
        text.extract_all(page, (
            ("title"     , '<h1 id="gn">', '</h1>'),
            ("title_jp"  , '<h1 id="gj">', '</h1>'),
            ("date"      , '>Posted:</td><td class="gdt2">', '</td>'),
            ("language"  , '>Language:</td><td class="gdt2">', ' '),
            ("gallery_size", '>File Size:</td><td class="gdt2">', '<'),
            ("count"     , '>Length:</td><td class="gdt2">', ' '),
        ), values=data)
        data["lang"] = util.language_to_code(data["language"])
        data["title"] = text.unescape(data["title"])
        data["title_jp"] = text.unescape(data["title_jp"])
        data["count"] = text.parse_int(data["count"])
        data["gallery_size"] = text.parse_bytes(
            data["gallery_size"].rstrip("Bb"))
        return data

    def get_images(self, page):
        """Collect url and metadata for all images in this gallery"""
        part = text.extract(page, 'hentai.org/s/', '"')[0]
        yield self.image_from_page(self.root + "/s/" + part)
        yield from self.images_from_api()

    def image_from_page(self, url):
        """Get image url and data from webpage"""
        self.wait()
        page = self.request(url).text
        data = text.extract_all(page, (
            (None      , '<div id="i3"><a onclick="return load_image(', ''),
            ("nextkey" , "'", "'"),
            ("url"     , '<img id="img" src="', '"'),
            ("origurl" , 'hentai.org/fullimg.php', '"'),
            ("originfo", 'ownload original', '<'),
            ("startkey", 'var startkey="', '";'),
            ("showkey" , 'var showkey="', '";'),
        ))[0]
        self.key["start"] = data["startkey"]
        self.key["show"] = data["showkey"]
        self.key["next"] = data["nextkey"]

        if self.original and data["origurl"]:
            part = text.unescape(data["origurl"])
            url = self.root + "/fullimg.php" + part
            info = self._parse_original_info(data["originfo"])
        else:
            url = data["url"]
            info = self._parse_image_info(url)

        info["num"] = 1
        info["image_token"] = data["startkey"]
        return url, text.nameext_from_url(data["url"], info)

    def images_from_api(self):
        """Get image url and data from api calls"""
        api_url = self.root + "/api.php"
        nextkey = self.key["next"]
        request = {
            "method" : "showpage",
            "gid"    : self.gid,
            "imgkey" : nextkey,
            "showkey": self.key["show"],
        }
        for request["page"] in range(2, self.count + 1):
            self.wait()
            page = self.request(api_url, method="POST", json=request).json()
            imgkey = nextkey
            nextkey, pos = text.extract(page["i3"], "'", "'")
            imgurl , pos = text.extract(page["i3"], 'id="img" src="', '"', pos)
            origurl, pos = text.extract(page["i7"], '<a href="', '"')

            if self.original and origurl:
                url = text.unescape(origurl)
                data = self._parse_original_info(
                    text.extract(page["i7"], "ownload original", "<", pos)[0]
                )
            else:
                url = imgurl
                data = self._parse_image_info(url)

            data["num"] = request["page"]
            data["image_token"] = imgkey
            yield url, text.nameext_from_url(imgurl, data)

            request["imgkey"] = nextkey

    @staticmethod
    def _parse_image_info(url):
        parts = url.split("/")[4].split("-")
        return {
            "width": text.parse_int(parts[2]),
            "height": text.parse_int(parts[3]),
            "size": text.parse_int(parts[1]),
        }

    @staticmethod
    def _parse_original_info(info):
        parts = info.lstrip().split(" ")
        return {
            "width": text.parse_int(parts[0]),
            "height": text.parse_int(parts[2]),
            "size": text.parse_bytes(parts[3] + parts[4][0]),
        }


class ExhentaiSearchExtractor(ExhentaiExtractor):
    """Extractor for exhentai search results"""
    subcategory = "search"
    pattern = [r"(?:https?://)?(?:g\.e-|e-|ex)hentai\.org/?\?(.*)$"]
    test = [
        ("https://exhentai.org/?f_search=touhou", None),
        ("https://exhentai.org/?f_doujinshi=0&f_manga=0&f_artistcg=0"
         "&f_gamecg=0&f_western=0&f_non-h=1&f_imageset=0&f_cosplay=0"
         "&f_asianporn=0&f_misc=0&f_search=touhou&f_apply=Apply+Filter", None),
    ]

    def __init__(self, match):
        ExhentaiExtractor.__init__(self)
        self.params = text.parse_query(match.group(1) or "")
        self.params["page"] = text.parse_int(self.params.get("page"))
        self.url = self.root

    def items(self):
        self.login()
        self.init()
        yield Message.Version, 1

        while True:
            page = self.request(self.url, params=self.params).text

            for row in text.extract_iter(page, '<tr class="gtr', '</tr>'):
                yield self._parse_row(row)

            if 'class="ptdd">&gt;<' in page or ">No hits found</p>" in page:
                return
            self.params["page"] += 1
            self.wait()

    def init(self):
        pass

    def _parse_row(self, row, extr=text.extract):
        """Parse information of a single result row"""
        gtype, pos = extr(row, ' alt="', '"')
        date , pos = extr(row, 'nowrap">', '<', pos)
        url  , pos = extr(row, ' class="it5"><a href="', '"', pos)
        title, pos = extr(row, '>', '<', pos)
        key , last = self._parse_last(row, pos)
        parts = url.rsplit("/", 3)

        return Message.Queue, url, {
            "type": gtype,
            "date": date,
            "gallery_id": text.parse_int(parts[1]),
            "gallery_token": parts[2],
            "title": text.unescape(title),
            key: last,
        }

    def _parse_last(self, row, pos):
        """Parse the last column of a result row"""
        return "uploader", text.remove_html(
            text.extract(row, '<td class="itu">', '</td>', pos)[0])


class ExhentaiFavoriteExtractor(ExhentaiSearchExtractor):
    """Extractor for favorited exhentai galleries"""
    subcategory = "favorite"
    pattern = [r"(?:https?://)?(?:g\.e-|e-|ex)hentai\.org"
               r"/favorites\.php(?:\?(.*))?"]
    test = [
        ("https://exhentai.org/favorites.php", None),
        ("https://exhentai.org/favorites.php?favcat=1&f_search=touhou"
         "&f_apply=Search+Favorites", None),
    ]

    def __init__(self, match):
        ExhentaiSearchExtractor.__init__(self, match)
        self.url = self.root + "/favorites.php"

    def init(self):
        # The first request to '/favorites.php' will return an empty list
        # if the 's' cookie isn't set (maybe on some other conditions as well),
        # so we make a "noop" request to get all the correct cookie values
        # and to get a filled favorite list on the next one.
        # TODO: proper cookie storage
        self.request(self.url)
        self.wait(1.5)

    def _parse_last(self, row, pos):
        return "date_favorited", text.extract(row, 'nowrap">', '<', pos)[0]
