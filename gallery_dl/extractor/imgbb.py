# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgbb.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache


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

        url = self.page_url
        params = {"sort": self.sort}
        while True:
            response = self.request(url, params=params, allow_redirects=False)
            if response.status_code < 300:
                break
            url = response.headers["location"]
            if url.startswith(self.root):
                raise exception.NotFoundError(self.subcategory)

        page = response.text
        data = self.metadata(page)
        first = True

        for img in self.images(page):
            image = {
                "id"       : img["url_viewer"].rpartition("/")[2],
                "user"     : img["user"]["username"] if "user" in img else "",
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
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=365*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/login"
        page = self.request(url).text
        token = text.extr(page, 'PF.obj.config.auth_token="', '"')

        headers = {"Referer": url}
        data = {
            "auth_token"   : token,
            "login-subject": username,
            "password"     : password,
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.history:
            raise exception.AuthenticationError()
        return self.cookies

    def _extract_resource(self, page):
        return util.json_loads(text.extr(
            page, "CHV.obj.resource=", "};") + "}")

    def _extract_user(self, page):
        return self._extract_resource(page).get("user") or {}

    def _pagination(self, page, endpoint, params):
        data = None
        seek, pos = text.extract(page, 'data-seek="', '"')
        tokn, pos = text.extract(page, 'PF.obj.config.auth_token="', '"', pos)
        params["action"] = "list"
        params["list"] = "images"
        params["sort"] = self.sort
        params["seek"] = seek
        params["page"] = 2
        params["auth_token"] = tokn

        while True:
            for img in text.extract_iter(page, "data-object='", "'"):
                yield util.json_loads(text.unquote(img))
            if data:
                if not data["seekEnd"] or params["seek"] == data["seekEnd"]:
                    return
                params["seek"] = data["seekEnd"]
                params["page"] += 1
            elif not seek or 'class="pagination-next"' not in page:
                return
            data = self.request(endpoint, method="POST", data=params).json()
            page = data["html"]


class ImgbbAlbumExtractor(ImgbbExtractor):
    """Extractor for albums on imgbb.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user}", "{album_name} {album_id}")
    pattern = r"(?:https?://)?ibb\.co/album/([^/?#]+)/?(?:\?([^#]+))?"
    example = "https://ibb.co/album/ID"

    def __init__(self, match):
        ImgbbExtractor.__init__(self, match)
        self.album_name = None
        self.album_id = match.group(1)
        self.sort = text.parse_query(match.group(2)).get("sort", "date_desc")
        self.page_url = "https://ibb.co/album/" + self.album_id

    def metadata(self, page):
        album = text.extr(page, '"og:title" content="', '"')
        user = self._extract_user(page)
        return {
            "album_id"   : self.album_id,
            "album_name" : text.unescape(album),
            "user"       : user.get("username") or "",
            "user_id"    : user.get("id") or "",
            "displayname": user.get("name") or "",
        }

    def images(self, page):
        url = text.extr(page, '"og:url" content="', '"')
        album_id = url.rpartition("/")[2].partition("?")[0]

        return self._pagination(page, "https://ibb.co/json", {
            "from"      : "album",
            "albumid"   : album_id,
            "params_hidden[list]"   : "images",
            "params_hidden[from]"   : "album",
            "params_hidden[albumid]": album_id,
        })


class ImgbbUserExtractor(ImgbbExtractor):
    """Extractor for user profiles in imgbb.com"""
    subcategory = "user"
    pattern = r"(?:https?://)?([\w-]+)\.imgbb\.com/?(?:\?([^#]+))?$"
    example = "https://USER.imgbb.com"

    def __init__(self, match):
        ImgbbExtractor.__init__(self, match)
        self.user = match.group(1)
        self.sort = text.parse_query(match.group(2)).get("sort", "date_desc")
        self.page_url = "https://{}.imgbb.com/".format(self.user)

    def metadata(self, page):
        user = self._extract_user(page)
        return {
            "user"       : user.get("username") or self.user,
            "user_id"    : user.get("id") or "",
            "displayname": user.get("name") or "",
        }

    def images(self, page):
        user = text.extr(page, '.obj.resource={"id":"', '"')
        return self._pagination(page, self.page_url + "json", {
            "from"      : "user",
            "userid"    : user,
            "params_hidden[userid]": user,
            "params_hidden[from]"  : "user",
        })


class ImgbbImageExtractor(ImgbbExtractor):
    subcategory = "image"
    pattern = r"(?:https?://)?ibb\.co/(?!album/)([^/?#]+)"
    example = "https://ibb.co/ID"

    def __init__(self, match):
        ImgbbExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def items(self):
        url = "https://ibb.co/" + self.image_id
        page = self.request(url).text
        extr = text.extract_from(page)
        user = self._extract_user(page)

        image = {
            "id"    : self.image_id,
            "title" : text.unescape(extr(
                '"og:title" content="', ' hosted at ImgBB"')),
            "url"   : extr('"og:image" content="', '"'),
            "width" : text.parse_int(extr('"og:image:width" content="', '"')),
            "height": text.parse_int(extr('"og:image:height" content="', '"')),
            "user"       : user.get("username") or "",
            "user_id"    : user.get("id") or "",
            "displayname": user.get("name") or "",
        }
        image["extension"] = text.ext_from_url(image["url"])

        yield Message.Directory, image
        yield Message.Url, image["url"], image
