# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgbb.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import json


class ImgbbExtractor(Extractor):
    """Base class for imgbb extractors"""
    category = "imgbb"
    filename_fmt = "{title} {id}.{extension}"
    archive_fmt = "{id}"
    root = "https://imgbb.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_url = self.sort = None

    def items(self):
        self.login()
        page = self.request(self.page_url, params={"sort": self.sort}).text
        data = self.metadata(page)
        first = True

        yield Message.Version, 1
        for img in self.images(page):
            image = {
                "id"       : img["url_viewer"].rpartition("/")[2],
                "user"     : img["user"]["username"],
                "title"    : text.unescape(img["title"]),
                "url"      : img["image"]["url"],
                "extension": img["image"]["extension"],
                "size"     : text.parse_int(img["image"]["size"]),
                "width"    : text.parse_int(img["width"]),
                "height"   : text.parse_int(img["height"]),
            }
            image.update(data)
            if first:
                first = False
                yield Message.Directory, data
            yield Message.Url, image["url"], image

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/login"
        page = self.request(url).text
        token = text.extract(page, 'PF.obj.config.auth_token="', '"')[0]

        headers = {"Referer": url}
        data = {
            "auth_token"   : token,
            "login-subject": username,
            "password"     : password,
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.history:
            raise exception.AuthenticationError()
        return self.session.cookies

    def _pagination(self, page, endpoint, params):
        params["page"] = 2
        data = None

        while True:
            for img in text.extract_iter(page, "data-object='", "'"):
                yield json.loads(text.unquote(img))
            if data:
                if params["seek"] == data["seekEnd"]:
                    return
                params["seek"] = data["seekEnd"]
                params["page"] += 1
            data = self.request(endpoint, "POST", data=params).json()
            page = data["html"]


class ImgbbAlbumExtractor(ImgbbExtractor):
    """Extractor for albums on imgbb.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user}", "{album_name} {album_id}")
    pattern = r"(?:https?://)?ibb\.co/album/([^/?&#]+)/?(?:\?([^#]+))?"
    test = (
        ("https://ibb.co/album/c6p5Yv", {
            "range": "1-80",
            "url": "8adaf0f7dfc19ff8bc4712c97f534af8b1e06412",
            "keyword": "155b665a53e83d359e914cab7c69d5b829444d64",
        }),
        ("https://ibb.co/album/c6p5Yv?sort=title_asc", {
            "range": "1-80",
            "url": "d6c45041d5c8323c435b183a976f3fde2af7c547",
            "keyword": "30c3262214e2044bbcf6bf2dee8e3ca7ebd62b71",
        }),
    )

    def __init__(self, match):
        ImgbbExtractor.__init__(self, match)
        self.album_name = None
        self.album_id = match.group(1)
        self.sort = text.parse_query(match.group(2)).get("sort", "date_desc")
        self.page_url = "https://ibb.co/album/" + self.album_id

    def metadata(self, page):
        album, pos = text.extract(page, '"og:title" content="', '"')
        user , pos = text.extract(page, 'rel="author">', '<', pos)
        return {
            "album_id"  : self.album_id,
            "album_name": text.unescape(album),
            "user"      : user.lower(),
        }

    def images(self, page):
        seek, pos = text.extract(page, 'data-seek="', '"')
        tokn, pos = text.extract(page, 'PF.obj.config.auth_token="', '"', pos)

        return self._pagination(page, "https://ibb.co/json", {
            "action"    : "list",
            "list"      : "images",
            "from"      : "album",
            "sort"      : self.sort,
            "albumid"   : self.album_id,
            "seek"      : seek,
            "auth_token": tokn,
            "params_hidden[list]"   : "images",
            "params_hidden[from]"   : "album",
            "params_hidden[albumid]": self.album_id,
        })


class ImgbbUserExtractor(ImgbbExtractor):
    """Extractor for user profiles in imgbb.com"""
    subcategory = "user"
    directory_fmt = ("{category}", "{user}")
    pattern = r"(?:https?://)?([^.]+)\.imgbb\.com/?(?:\?([^#]+))?$"
    test = ("https://folkie.imgbb.com", {
        "range": "1-80",
        "pattern": r"https?://i\.ibb\.co/\w+/[^/?&#]+",
    })

    def __init__(self, match):
        ImgbbExtractor.__init__(self, match)
        self.user = match.group(1)
        self.sort = text.parse_query(match.group(2)).get("sort", "date_desc")
        self.page_url = "https://{}.imgbb.com/".format(self.user)

    def metadata(self, page):
        return {"user": self.user}

    def images(self, page):
        seek, pos = text.extract(page, 'data-seek="', '"')
        tokn, pos = text.extract(page, 'PF.obj.config.auth_token="', '"', pos)
        user, pos = text.extract(page, '.obj.resource={"id":"', '"', pos)

        return self._pagination(page, self.page_url + "json", {
            "action"    : "list",
            "list"      : "images",
            "from"      : "user",
            "sort"      : self.sort,
            "seek"      : seek,
            "userid"    : user,
            "auth_token": tokn,
            "params_hidden[userid]": user,
            "params_hidden[from]"  : "user",
        })
