# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.zerochan.net/"""

from .booru import BooruExtractor
from ..cache import cache
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?zerochan\.net"


class ZerochanExtractor(BooruExtractor):
    """Base class for zerochan extractors"""
    category = "zerochan"
    root = "https://www.zerochan.net"
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    cookiedomain = ".zerochan.net"
    cookienames = ("z_id", "z_hash")

    def login(self):
        self._logged_in = True
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if username:
                self._update_cookies(self._login_impl(username, password))
            else:
                self._logged_in = False

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/login"
        headers = {
            "Origin"  : self.root,
            "Referer" : url,
        }
        data = {
            "ref"     : "/",
            "name"    : username,
            "password": password,
            "login"   : "Login",
        }

        response = self.request(url, method="POST", headers=headers, data=data)
        if not response.history:
            raise exception.AuthenticationError()

        return response.cookies

    def _parse_entry_html(self, entry_id):
        url = "{}/{}".format(self.root, entry_id)
        extr = text.extract_from(self.request(url).text)

        data = {
            "id"      : text.parse_int(entry_id),
            "author"  : extr('"author": "', '"'),
            "file_url": extr('"contentUrl": "', '"'),
            "date"    : text.parse_datetime(extr('"datePublished": "', '"')),
            "width"   : text.parse_int(extr('"width": "', ' ')),
            "height"  : text.parse_int(extr('"height": "', ' ')),
            "size"    : text.parse_bytes(extr('"contentSize": "', 'B')),
            "path"    : text.split_html(extr(
                'class="breadcrumbs', '</p>'))[2:],
            "uploader": extr('href="/user/', '"'),
            "tags"    : extr('<ul id="tags"', '</ul>'),
            "source"  : extr('<h2>Source</h2>', '</p><h2>').rpartition(
                ">")[2] or None,
        }

        html = data["tags"]
        tags = data["tags"] = []
        for tag in html.split("<li class=")[1:]:
            category, _, name = text.extr(tag, 'alt="', '<').partition('">')
            tags.append(category + ":" + name.strip())

        return data

    def _parse_entry_json(self, entry_id):
        url = "{}/{}?json".format(self.root, entry_id)
        item = self.request(url).json()

        data = {
            "id"      : item["id"],
            "file_url": item["full"],
            "width"   : item["width"],
            "height"  : item["height"],
            "size"    : item["size"],
            "name"    : item["primary"],
            "md5"     : item["hash"],
            "source"  : item.get("source"),
        }

        if not self._logged_in:
            data["tags"] = item["tags"]

        return data


class ZerochanTagExtractor(ZerochanExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"/(?!\d+$)([^/?#]+)/?(?:\?([^#]+))?"
    test = ("https://www.zerochan.net/Perth+%28Kantai+Collection%29", {
        "pattern": r"https://static\.zerochan\.net/.+\.full\.\d+\.(jpg|png)",
        "count": "> 24",
        "keyword": {
            "extension": r"re:jpg|png",
            "file_url": r"re:https://static\.zerochan\.net"
                        r"/.+\.full\.\d+\.(jpg|png)",
            "filename": r"re:(Perth\.\(Kantai\.Collection\)"
                        r"|Kantai\.Collection)\.full\.\d+",
            "height": r"re:^\d+$",
            "id": r"re:^\d+$",
            "name": r"re:(Perth \(Kantai Collection\)|Kantai Collection)",
            "search_tags": "Perth (Kantai Collection)",
            "size": r"re:^\d+k$",
            "width": r"re:^\d+$",
        },
    })

    def __init__(self, match):
        ZerochanExtractor.__init__(self, match)
        self.search_tag, self.query = match.groups()

    def metadata(self):
        return {"search_tags": text.unquote(
            self.search_tag.replace("+", " "))}

    def posts(self):
        url = self.root + "/" + self.search_tag
        params = text.parse_query(self.query)
        params["p"] = text.parse_int(params.get("p"), 1)
        metadata = self.config("metadata")

        while True:
            page = self.request(url, params=params).text
            thumbs = text.extr(page, '<ul id="thumbs', '</ul>')
            extr = text.extract_from(thumbs)

            while True:
                post = extr('<li class="', '>')
                if not post:
                    break

                if metadata:
                    entry_id = extr('href="/', '"')
                    post = self._parse_entry_html(entry_id)
                    post.update(self._parse_entry_json(entry_id))
                    yield post
                else:
                    yield {
                        "id"    : extr('href="/', '"'),
                        "name"  : extr('alt="', '"'),
                        "width" : extr('title="', 'x'),
                        "height": extr('', ' '),
                        "size"  : extr('', 'B'),
                        "file_url": "https://static." + extr(
                            '<a href="https://static.', '"'),
                    }

            if 'rel="next"' not in page:
                break
            params["p"] += 1


class ZerochanImageExtractor(ZerochanExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/(\d+)"
    test = ("https://www.zerochan.net/2920445", {
        "pattern": r"https://static\.zerochan\.net/"
                   r"Perth\.%28Kantai\.Collection%29\.full.2920445\.jpg",
        "keyword": {
            "author": "YeFan 葉凡",
            "date": "dt:2020-04-24 21:33:44",
            "file_url": "https://static.zerochan.net"
                        "/Perth.%28Kantai.Collection%29.full.2920445.jpg",
            "filename": "Perth.(Kantai.Collection).full.2920445",
            "height": 1366,
            "id": 2920445,
            "path": ["Kantai Collection", "Perth (Kantai Collection)"],
            "size": 1975296,
            "tags": [
                "Mangaka:YeFan 葉凡",
                "Game:Kantai Collection",
                "Character:Perth (Kantai Collection)",
                "Theme:Blonde Hair",
                "Theme:Braids",
                "Theme:Coat",
                "Theme:Female",
                "Theme:Firefighter Outfit",
                "Theme:Group",
                "Theme:Long Sleeves",
                "Theme:Personification",
                "Theme:Pins",
                "Theme:Ribbon",
                "Theme:Shirt",
                "Theme:Short Hair",
            ],
            "uploader": "YukinoTokisaki",
            "width": 1920,
        },
    })

    def __init__(self, match):
        ZerochanExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def posts(self):
        post = self._parse_entry_html(self.image_id)
        if self.config("metadata"):
            post.update(self._parse_entry_json(self.image_id))
        return (post,)
