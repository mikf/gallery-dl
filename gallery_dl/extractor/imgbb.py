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
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{title} {id}.{extension}"
    archive_fmt = "{id}"
    root = "https://imgbb.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_url = self.sort = None

    def items(self):
        self.login()
        response = self.request(self.page_url, params={"sort": self.sort})
        if response.history and response.url.startswith(self.root):
            raise exception.NotFoundError(self.subcategory)
        page = response.text
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
            data = self.request(endpoint, method="POST", data=params).json()
            page = data["html"]


class ImgbbAlbumExtractor(ImgbbExtractor):
    """Extractor for albums on imgbb.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user}", "{album_name} {album_id}")
    pattern = r"(?:https?://)?ibb\.co/album/([^/?&#]+)/?(?:\?([^#]+))?"
    test = (
        ("https://ibb.co/album/i5PggF", {
            "range": "1-80",
            "url": "570872b6eb3e11cf10b618922b780fed204c3f09",
            "keyword": "0f2fc956728c36540c577578bd168d2459d6ae4b",
        }),
        ("https://ibb.co/album/i5PggF?sort=title_asc", {
            "range": "1-80",
            "url": "e2e387b8fdb3690bd75d804d0af2833112e385cd",
            "keyword": "a307fc9d2085bdc0eb7c538c8d866c59198d460c",
        }),
        # deleted
        ("https://ibb.co/album/fDArrF", {
            "exception": exception.NotFoundError,
        }),
        # private
        ("https://ibb.co/album/hqgWrF", {
            "exception": exception.HttpError,
        })
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


class ImgbbImageExtractor(ImgbbExtractor):
    subcategory = "image"
    pattern = r"(?:https?://)?ibb\.co/(?!album/)([^/?&#]+)"
    test = ("https://ibb.co/fUqh5b", {
        "pattern": "https://image.ibb.co/dY5FQb/Arundel-Ireeman-5.jpg",
        "content": "c5a0965178a8b357acd8aa39660092918c63795e",
        "keyword": {
            "id"    : "fUqh5b",
            "title" : "Arundel Ireeman 5",
            "url"   : "https://image.ibb.co/dY5FQb/Arundel-Ireeman-5.jpg",
            "width" : 960,
            "height": 719,
            "user"  : "folkie",
            "extension": "jpg",
        },
    })

    def __init__(self, match):
        ImgbbExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def items(self):
        url = "https://ibb.co/" + self.image_id
        extr = text.extract_from(self.request(url).text)

        image = {
            "id"    : self.image_id,
            "title" : text.unescape(extr('"og:title" content="', '"')),
            "url"   : extr('"og:image" content="', '"'),
            "width" : text.parse_int(extr('"og:image:width" content="', '"')),
            "height": text.parse_int(extr('"og:image:height" content="', '"')),
            "user"  : extr('rel="author">', '<').lower(),
        }
        image["extension"] = text.ext_from_url(image["url"])

        yield Message.Version, 1
        yield Message.Directory, image
        yield Message.Url, image["url"], image
