# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
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
import requests


class ExhentaiGalleryExtractor(Extractor):
    """Extractor for image galleries from exhentai.org"""
    category = "exhentai"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery_id}"]
    filename_fmt = "{gallery_id}_{num:>04}_{image_token}_{name}.{extension}"
    pattern = [r"(?:https?://)?(g\.e-|e-|ex)hentai\.org/g/(\d+)/([\da-f]{10})"]
    test = [
        ("https://exhentai.org/g/960460/4f0e369d82/", {
            "keyword": "173277161e28162dcc755d2e7a88e6cd750f2477",
            "content": "493d759de534355c9f55f8e365565b62411de146",
        }),
        ("https://exhentai.org/g/960461/4f0e369d82/", {
            "exception": exception.NotFoundError,
        }),
        ("http://exhentai.org/g/962698/7f02358e00/", {
            "exception": exception.AuthorizationError,
        }),
    ]
    root = "https://exhentai.org"
    cookienames = ("ipb_member_id", "ipb_pass_hash")
    cookiedomain = ".exhentai.org"

    def __init__(self, match):
        Extractor.__init__(self)
        self.key = {}
        self.count = 0
        self.version, self.gid, self.token = match.groups()
        self.gid = util.safe_int(self.gid)
        self.original = self.config("original", True)
        self.wait_min = self.config("wait-min", 3)
        self.wait_max = self.config("wait-max", 6)
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": self.root + "/",
        })

    def items(self):
        self.login()
        yield Message.Version, 1

        url = "{}/g/{}/{}/".format(self.root, self.gid, self.token)
        response = self.request(url, fatal=False)
        page = response.text

        if response.status_code == 404 and "Gallery Not Available" in page:
            raise exception.AuthorizationError()
        if self._is_sadpanda(response):
            self.log.info("sadpanda.jpg")
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
            ("size"      , '>File Size:</td><td class="gdt2">', ' '),
            ("size_units", '', '<'),
            ("count"     , '>Length:</td><td class="gdt2">', ' '),
        ), values=data)
        data["lang"] = util.language_to_code(data["language"])
        data["title"] = text.unescape(data["title"])
        data["title_jp"] = text.unescape(data["title_jp"])
        data["count"] = util.safe_int(data["count"])
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
            ("startkey", 'var startkey="', '";'),
            ("showkey" , 'var showkey="', '";'),
        ))[0]
        self.key["start"] = data["startkey"]
        self.key["show"] = data["showkey"]
        self.key["next"] = data["nextkey"]

        if self.original and data["origurl"]:
            part = text.unescape(data["origurl"])
            url = self.root + "/fullimg.php" + part
        else:
            url = data["url"]

        return url, text.nameext_from_url(data["url"], {
            "num": 1,
            "image_token": data["startkey"],
        })

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
            while True:
                try:
                    self.wait()
                    page = self.session.post(api_url, json=request).json()
                    break
                except requests.exceptions.ConnectionError:
                    pass
            imgkey = nextkey
            nextkey, pos = text.extract(page["i3"], "'", "'")
            imgurl , pos = text.extract(page["i3"], 'id="img" src="', '"', pos)
            origurl, pos = text.extract(page["i7"], '<a href="', '"')

            if self.original and origurl:
                url = text.unescape(origurl)
            else:
                url = imgurl

            yield url, text.nameext_from_url(imgurl, {
                "num": request["page"],
                "image_token": imgkey
            })
            request["imgkey"] = nextkey

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
