# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at https://exhentai.org/"""

from .common import Extractor, Message
from .. import config, text, iso639_1, exception
from ..cache import cache
import time
import random
import requests


class ExhentaiGalleryExtractor(Extractor):
    """Extractor for image-galleries from exhentai.org"""
    category = "exhentai"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery-id}"]
    filename_fmt = "{gallery-id}_{num:>04}_{image-token}_{name}.{extension}"
    pattern = [r"(?:https?://)?(?:g\.e-|ex)hentai\.org/g/(\d+)/([\da-f]{10})"]
    test = [
        ("https://exhentai.org/g/960460/4f0e369d82/", {
            "keyword": "623f8c86c9fe38e964682dd4309b96922655b900",
            "content": "493d759de534355c9f55f8e365565b62411de146",
        }),
        ("https://exhentai.org/g/960461/4f0e369d82/", {
            "exception": exception.NotFoundError,
        }),
        ("http://exhentai.org/g/962698/7f02358e00/", {
            "exception": exception.AuthorizationError,
        }),
    ]
    api_url = "https://exhentai.org/api.php"

    def __init__(self, match):
        Extractor.__init__(self)
        self.key = {}
        self.count = 0
        self.gid, self.token = match.groups()
        self.original = config.interpolate(
            ("extractor", "exhentai", "download-original"), True)
        self.wait_min = config.interpolate(
            ("extractor", "exhentai", "wait-min"), 3)
        self.wait_max = config.interpolate(
            ("extractor", "exhentai", "wait-max"), 6)
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min

    def items(self):
        self.login()
        yield Message.Version, 1
        yield Message.Headers, self.setup_headers()
        yield Message.Cookies, self.session.cookies

        url = "https://exhentai.org/g/{}/{}/".format(self.gid, self.token)
        response = self.session.get(url)
        page = response.text
        if response.status_code == 404 and "Gallery Not Available" in page:
            raise exception.AuthorizationError()
        if page.startswith(("\ufeffKey missing", "\ufeffGallery not found")):
            raise exception.NotFoundError("gallery")
        data = self.get_job_metadata(page)
        self.count = int(data["count"])
        yield Message.Directory, data

        for url, image in self.get_images(page):
            data.update(image)
            if "/fullimg.php" in url:
                data["extension"] = ""
                self.wait((1, 2))
            yield Message.Url, url, data

    def setup_headers(self):
        """Initialize headers"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,"
                      "application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://exhentai.org/",
        })
        headers = self.session.headers.copy()
        headers["Accept"] = "image/png,image/*;q=0.8,*/*;q=0.5"
        return headers

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "gallery-id"   : self.gid,
            "gallery-token": self.token,
        }
        text.extract_all(page, (
            ("title"     , '<h1 id="gn">', '</h1>'),
            ("title_jp"  , '<h1 id="gj">', '</h1>'),
            ("date"      , '>Posted:</td><td class="gdt2">', '</td>'),
            ("language"  , '>Language:</td><td class="gdt2">', ' '),
            ("size"      , '>File Size:</td><td class="gdt2">', ' '),
            ("size-units", '', '<'),
            ("count"     , '>Length:</td><td class="gdt2">', ' '),
        ), values=data)
        data["lang"] = iso639_1.language_to_code(data["language"])
        data["title"] = text.unescape(data["title"])
        data["title_jp"] = text.unescape(data["title_jp"])
        return data

    def get_images(self, page):
        """Collect url and metadata for all images in this gallery"""
        part = text.extract(page, 'hentai.org/s/', '"')[0]
        yield self.image_from_page("https://exhentai.org/s/" + part)
        yield from self.images_from_api()

    def image_from_page(self, url):
        """Get image url and data from webpage"""
        self.wait()
        page = self.request(url).text
        data = text.extract_all(page, (
            (None      , '<div id="i3"><a onclick="return load_image(', ''),
            ("nextkey" , "'", "'"),
            ("url"     , '<img id="img" src="', '"'),
            ("origurl" , 'https://exhentai.org/fullimg.php', '"'),
            ("startkey", 'var startkey="', '";'),
            ("showkey" , 'var showkey="', '";'),
        ))[0]
        self.key["start"] = data["startkey"]
        self.key["show"] = data["showkey"]
        self.key["next"] = data["nextkey"]

        if self.original and data["origurl"]:
            part = text.unescape(data["origurl"])
            url = "https://exhentai.org/fullimg.php" + part
        else:
            url = data["url"]

        return url, text.nameext_from_url(data["url"], {
            "num": 1,
            "image-token": data["startkey"],
        })

    def images_from_api(self):
        """Get image url and data from api calls"""
        nextkey = self.key["next"]
        request = {
            "method" : "showpage",
            "gid"    : int(self.gid),
            "imgkey" : nextkey,
            "showkey": self.key["show"],
        }
        for request["page"] in range(2, self.count + 1):
            while True:
                try:
                    self.wait()
                    page = self.session.post(self.api_url, json=request).json()
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
                "image-token": imgkey
            })
            request["imgkey"] = nextkey

    def wait(self, waittime=None):
        """Wait for a randomly chosen amount of seconds"""
        if not waittime:
            waittime = random.uniform(self.wait_min, self.wait_max)
        else:
            waittime = random.uniform(*waittime)
        time.sleep(waittime)

    def login(self):
        """Login and set necessary cookies"""
        username = config.interpolate(("extractor", "exhentai", "username"))
        password = config.interpolate(("extractor", "exhentai", "password"))
        cookies = self._login_impl(username, password)
        for key, value in cookies.items():
            self.session.cookies.set(
                key, value, domain=".exhentai.org", path="/")

    @cache(maxage=360*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        cnames = ["ipb_member_id", "ipb_pass_hash"]

        try:
            cookies = config.get(("extractor", "exhentai", "cookies"))
            if isinstance(cookies, dict) and all(c in cookies for c in cnames):
                return cookies
        except TypeError:
            pass

        url = "https://forums.e-hentai.org/index.php?act=Login&CODE=01"
        params = {
            "CookieDate": "1",
            "b": "d",
            "bt": "1-1",
            "UserName": username,
            "PassWord": password,
            "ipb_login_submit": "Login!",
        }
        referer = "http://e-hentai.org/bounce_login.php?b=d&bt=1-1"
        self.session.headers["Referer"] = referer
        response = self.session.post(url, data=params)

        if "You are now logged in as:" not in response.text:
            raise exception.AuthenticationError()
        return {c: response.cookies[c] for c in cnames}
