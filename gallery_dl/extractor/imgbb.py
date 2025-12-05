# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
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
    directory_fmt = ("{category}", "{user[name]:?//}{user[id]:? (/)/}",
                     "{album[title]} ({album[id]})")
    filename_fmt = "{title} ({id}).{extension}"
    archive_fmt = "{user[id]} {id}"
    cookies_domain = ".imgbb.com"
    cookies_names = ("PHPSESSID", "LID")
    root = "https://ibb.co"

    def items(self):
        self.login()

        for image in self.posts():
            url = image["url"]
            text.nameext_from_url(url, image)
            yield Message.Directory, "", image
            yield Message.Url, url, image

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

    @cache(maxage=365*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "https://imgbb.com/login"
        page = self.request(url).text
        token = text.extr(page, 'name="auth_token" value="', '"')

        headers = {
            "Referer": url,
        }
        data = {
            "auth_token"   : token,
            "login-subject": username,
            "password"     : password,
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.history:
            raise exception.AuthenticationError()
        return self.cookies

    def _pagination(self, page, url, params):
        seek, pos = text.extract(page, 'data-seek="', '"')
        tokn, pos = text.extract(page, 'PF.obj.config.auth_token="', '"', pos)
        resc, pos = text.extract(page, "CHV.obj.resource=", "};", pos)
        self.kwdict["user"] = util.json_loads(resc + "}").get("user")

        data = None
        while True:
            for obj in text.extract_iter(page, "data-object='", "'"):
                post = util.json_loads(text.unquote(obj))
                image = post["image"]
                image["filename"], image["name"] = \
                    image["name"], image["filename"]
                image["id"] = post["id_encoded"]
                image["title"] = post["title"]
                image["width"] = text.parse_int(post["width"])
                image["height"] = text.parse_int(post["height"])
                image["size"] = text.parse_int(image["size"])
                yield image

            if data:
                if not data["seekEnd"] or params["seek"] == data["seekEnd"]:
                    return
                params["seek"] = data["seekEnd"]
                params["page"] += 1
            elif not seek or 'class="pagination-next"' not in page:
                return
            else:
                params["action"] = "list"
                params["page"] = 2
                params["seek"] = seek
                params["auth_token"] = tokn

                headers = {
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Origin": self.root,
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                }

            data = self.request_json(
                url, method="POST", headers=headers, data=params)
            page = data["html"]


class ImgbbAlbumExtractor(ImgbbExtractor):
    """Extractor for imgbb albums"""
    subcategory = "album"
    pattern = r"(?:https?://)?ibb\.co/album/([^/?#]+)/?(?:\?([^#]+))?"
    example = "https://ibb.co/album/ID"

    def posts(self):
        album_id, qs = self.groups
        url = f"{self.root}/album/{album_id}"
        params = text.parse_query(qs)
        page = self.request(url, params=params).text
        extr = text.extract_from(page)

        self.kwdict["album"] = album = {
            "url": extr(
                'property="og:url" content="', '"'),
            "title": text.unescape(extr(
                'property="og:title" content="', '"')),
            "description": text.unescape(extr(
                'property="og:description" content="', '"')),
            "id": extr(
                'data-text="album-name" href="https://ibb.co/album/', '"'),
            "count": text.parse_int(extr(
                'data-text="image-count">', "<")),
        }

        url = f"{self.root}/json"
        params["pathname"] = f"/album/{album['id']}"
        return self._pagination(page, url, params)


class ImgbbImageExtractor(ImgbbExtractor):
    subcategory = "image"
    pattern = r"(?:https?://)?ibb\.co/([^/?#]+)"
    example = "https://ibb.co/ID"

    def posts(self):
        url = f"{self.root}/{self.groups[0]}"
        page = self.request(url).text
        extr = text.extract_from(page)

        image = {
            "id"    : extr('property="og:url" content="https://ibb.co/', '"'),
            "title" : text.unescape(extr(
                '"og:title" content="', ' hosted at ImgBB"')),
            "url"   : extr('"og:image" content="', '"'),
            "width" : text.parse_int(extr('"og:image:width" content="', '"')),
            "height": text.parse_int(extr('"og:image:height" content="', '"')),
            "album" : extr("Added to <a", "</a>"),
            "date"  : self.parse_datetime_iso(extr('<span title="', '"')),
            "user"  : util.json_loads(extr(
                "CHV.obj.resource=", "};") + "}").get("user"),
        }

        if album := image["album"]:
            image["album"] = {
                "id"   : text.extr(album, "/album/", '"'),
                "title": text.unescape(album.rpartition(">")[2]),
            }
        else:
            image["album"] = None

        return (image,)


class ImgbbUserExtractor(ImgbbExtractor):
    """Extractor for imgbb user profiles"""
    subcategory = "user"
    directory_fmt = ("{category}", "{user[name]} ({user[id]})")
    pattern = r"(?:https?://)?([\w-]+)\.imgbb\.com/?(?:\?([^#]+))?"
    example = "https://USER.imgbb.com"

    def posts(self):
        user, qs = self.groups
        url = f"https://{user}.imgbb.com/"
        params = text.parse_query(qs)
        response = self.request(url, params=params, allow_redirects=False)

        if response.status_code < 300:
            params["pathname"] = "/"
            return self._pagination(response.text, f"{url}json", params)

        if response.status_code == 301:
            raise exception.NotFoundError("user")
        redirect = f"HTTP redirect to {response.headers.get('Location')}"
        if response.status_code == 302:
            raise exception.AuthRequired(
                ("username & password", "authenticated cookies"),
                "profile", redirect)
        raise exception.AbortExtraction(redirect)
