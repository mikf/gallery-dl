# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.mangoxo.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import hashlib
import time


class MangoxoExtractor(Extractor):
    """Base class for mangoxo extractors"""
    category = "mangoxo"
    root = "https://www.mangoxo.com"
    cookiedomain = "www.mangoxo.com"
    cookienames = ("SESSION",)
    _warning = True

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))
        elif MangoxoExtractor._warning:
            MangoxoExtractor._warning = False
            self.log.warning("Unauthenticated users cannot see "
                             "more than 5 images per album")

    @cache(maxage=3*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/login"
        page = self.request(url).text
        token = text.extract(page, 'id="loginToken" value="', '"')[0]

        url = self.root + "/api/login"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.root + "/login",
        }
        data = self._sign_by_md5(username, password, token)
        response = self.request(url, method="POST", headers=headers, data=data)

        data = response.json()
        if str(data.get("result")) != "1":
            raise exception.AuthenticationError(data.get("msg"))
        return {"SESSION": self.session.cookies.get("SESSION")}

    @staticmethod
    def _sign_by_md5(username, password, token):
        # https://dns.mangoxo.com/libs/plugins/phoenix-ui/js/phoenix-ui.js
        params = [
            ("username" , username),
            ("password" , password),
            ("token"    , token),
            ("timestamp", str(int(time.time()))),
        ]
        query = "&".join("=".join(item) for item in sorted(params))
        query += "&secretKey=340836904"
        sign = hashlib.md5(query.encode()).hexdigest()
        params.append(("sign", sign.upper()))
        return params

    @staticmethod
    def _total_pages(page):
        return text.parse_int(text.extract(page, "total :", ",")[0])


class MangoxoAlbumExtractor(MangoxoExtractor):
    """Extractor for albums on mangoxo.com"""
    subcategory = "album"
    filename_fmt = "{album[id]}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{channel[name]}", "{album[name]}")
    archive_fmt = "{album[id]}_{num}"
    pattern = r"(?:https?://)?(?:www\.)?mangoxo\.com/album/(\w+)"
    test = ("https://www.mangoxo.com/album/lzVOv1Q9", {
        "url": "ad921fe62663b06e7d73997f7d00646cab7bdd0d",
        "keyword": {
            "channel": {
                "id": "gaxO16d8",
                "name": "Phoenix",
                "cover": str,
            },
            "album": {
                "id": "lzVOv1Q9",
                "name": "re:池永康晟 Ikenaga Yasunari 透出古朴",
                "date": "dt:2019-03-22 14:42:00",
                "description": str,
            },
            "id": int,
            "num": int,
            "count": 65,
        },
    })

    def __init__(self, match):
        MangoxoExtractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        self.login()
        url = "{}/album/{}/".format(self.root, self.album_id)
        page = self.request(url).text
        data = self.metadata(page)
        imgs = self.images(url, page)

        yield Message.Directory, data

        data["extension"] = None
        for data["num"], path in enumerate(imgs, 1):
            data["id"] = text.parse_int(text.extract(path, "=", "&")[0])
            url = self.root + "/external/" + path.rpartition("url=")[2]
            yield Message.Url, url, text.nameext_from_url(url, data)

    def metadata(self, page):
        """Return general metadata"""
        extr = text.extract_from(page)
        title = extr('<img id="cover-img" alt="', '"')
        cid = extr('href="https://www.mangoxo.com/user/', '"')
        cname = extr('<img alt="', '"')
        cover = extr(' src="', '"')
        count = extr('id="pic-count">', '<')
        date = extr('class="fa fa-calendar"></i>', '<')
        descr = extr('<pre>', '</pre>')

        return {
            "channel": {
                "id": cid,
                "name": text.unescape(cname),
                "cover": cover,
            },
            "album": {
                "id": self.album_id,
                "name": text.unescape(title),
                "date": text.parse_datetime(date.strip(), "%Y.%m.%d %H:%M"),
                "description": text.unescape(descr),
            },
            "count": text.parse_int(count),
        }

    def images(self, url, page):
        """Generator; Yields all image URLs"""
        total = self._total_pages(page)
        num = 1

        while True:
            yield from text.extract_iter(
                page, 'class="lightgallery-item" href="', '"')
            if num >= total:
                return
            num += 1
            page = self.request(url + str(num)).text


class MangoxoChannelExtractor(MangoxoExtractor):
    """Extractor for all albums on a mangoxo channel"""
    subcategory = "channel"
    pattern = r"(?:https?://)?(?:www\.)?mangoxo\.com/(\w+)/album"
    test = ("https://www.mangoxo.com/phoenix/album", {
        "pattern": MangoxoAlbumExtractor.pattern,
        "range": "1-30",
        "count": "> 20",
    })

    def __init__(self, match):
        MangoxoExtractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        self.login()
        num = total = 1
        url = "{}/{}/album/".format(self.root, self.user)
        data = {"_extractor": MangoxoAlbumExtractor}

        while True:
            page = self.request(url + str(num)).text

            for album in text.extract_iter(
                    page, '<a class="link black" href="', '"'):
                yield Message.Queue, album, data

            if num == 1:
                total = self._total_pages(page)
            if num >= total:
                return
            num += 1
