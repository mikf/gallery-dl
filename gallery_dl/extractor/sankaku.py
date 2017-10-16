# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://chan.sankakucomplex.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import time
import random


class SankakuTagExtractor(Extractor):
    """Extractor for images from chan.sankakucomplex.com by search-tags"""
    category = "sankaku"
    subcategory = "tag"
    directory_fmt = ["{category}", "{tags}"]
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    pattern = [r"(?:https?://)?chan\.sankakucomplex\.com"
               r"/\?(?:[^&#]*&)*tags=([^&#]+)"]
    test = [("https://chan.sankakucomplex.com/?tags=bonocho", {
        "count": 5,
        "pattern": (r"https://cs\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}"
                    r"/[^/]{32}\.\w+\?e=\d+&m=[^&#]+"),
    })]
    root = "https://chan.sankakucomplex.com"
    cookienames = ("login", "pass_hash")
    cookiedomain = "chan.sankakucomplex.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.logged_in = True
        self.pagestart = 1
        self.tags = text.unquote(match.group(1).replace("+", " "))
        self.wait_min = self.config("wait-min", 2)
        self.wait_max = self.config("wait-max", 4)
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 Gecko/20100101 Firefox/40.0"
        )

    def skip(self, num):
        pages = min(num // 20, 49)
        self.pagestart += pages
        return pages * 20

    def items(self):
        self.login()
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for image in self.get_images():
            image.update(data)
            yield Message.Url, image["file_url"], image

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {"tags": self.tags}

    def get_images(self):
        """Yield all available images for the given tags"""
        params = {
            "tags": self.tags,
            "page": self.pagestart,
        }
        while self.logged_in or params["page"] <= 25:
            image = None
            page = self.request(self.root, params=params, retries=10).text
            pos = text.extract(page, '<div id=more-popular-posts-link>', '')[1]
            for image_id in text.extract_iter(
                    page, '<span class="thumb blacklisted" id=p', '>', pos):
                self.wait()
                image = self.get_image_metadata(image_id)
                yield image
            if not image:
                return
            params["page"] += 1
            params["next"] = image["id"] - 1
        self.log.warning(
            "Unauthenticated users may only access the first 500 images / 25 "
            "pages. (Use '--range 501-' to continue downloading from this "
            "point onwards after setting up an account.)")

    def get_image_metadata(self, image_id):
        """Collect metadata for a single image"""
        url = "https://chan.sankakucomplex.com/post/show/" + image_id
        page = self.request(url, retries=10).text
        image_url, pos = text.extract(page, '<li>Original: <a href="', '"')
        width    , pos = text.extract(page, '>', 'x', pos)
        height   , pos = text.extract(page, '', ' ', pos)
        data = text.nameext_from_url(image_url, {
            "id": util.safe_int(image_id),
            "file_url": "https:" + text.unescape(image_url),
            "width": util.safe_int(width),
            "height": util.safe_int(height),
        })
        data["md5"] = data["name"]
        return data

    def wait(self):
        """Wait for a randomly chosen amount of seconds"""
        time.sleep(random.uniform(self.wait_min, self.wait_max))

    def login(self):
        """Login and set necessary cookies"""
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            cookies = self._login_impl(username, password)
            for key, value in cookies.items():
                self.session.cookies.set(
                    key, value, domain=self.cookiedomain)
        else:
            self.logged_in = False

    @cache(maxage=90*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        self.log.info("Logging in as %s", username)
        params = {
            "url": "",
            "user[name]": username,
            "user[password]": password,
            "commit": "Login",
        }
        response = self.request(self.root + "/user/authenticate",
                                method="POST", params=params)
        if not response.history or response.url != self.root + "/user/home":
            raise exception.AuthenticationError()
        cookies = response.history[0].cookies
        return {c: cookies[c] for c in self.cookienames}
