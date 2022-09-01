# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.zerochan.net/"""

from .booru import BooruExtractor
from ..cache import cache
from .. import text, exception
from xml.etree import ElementTree


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
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if username:
                self._update_cookies(self._login_impl(username, password))
        # force legacy layout
        self.session.cookies.set("v3", "0", domain=self.cookiedomain)

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

        return {
            "id"    : entry_id,
            "author": extr('"author": "', '"'),
            "file_url": extr('"contentUrl": "', '"'),
            "date"  : text.parse_datetime(extr(
                '"datePublished": "', '"'), "%a %b %d %H:%M:%S %Y"),
            "width" : extr('"width": "', ' '),
            "height": extr('"height": "', ' '),
            "size"  : text.parse_bytes(extr('"contentSize": "', 'B')),
            "path"  : text.split_html(extr(
                'class="breadcrumbs', '</p>'))[3::2],
            "tags"  : extr('alt="Tags: Anime, ', '"').split(", ")
        }

    def _parse_entry_xml(self, entry_id):
        url = "{}/{}?xml".format(self.root, entry_id)
        item = ElementTree.fromstring(self.request(url).text)[0][-1]
        #  content = item[4].attrib

        return {
            #  "id"    : entry_id,
            #  "file_url": content["url"],
            #  "width" : content["width"],
            #  "height": content["height"],
            #  "size"  : content["filesize"],
            "name"  : item[2].text,
            "tags"  : item[5].text.lstrip().split(", "),
            "md5"   : item[6].text,
        }


class ZerochanTagExtractor(ZerochanExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"/(?!\d+$)([^/?#]+)/?(?:\?([^#]+))?"
    test = ("https://www.zerochan.net/Perth+%28Kantai+Collection%29", {
        "pattern": r"https://static\.zerochan\.net/.+\.full\.\d+\.(jpg|png)",
        "count": "> 24",
        "keywords": {
            "extension": r"re:jpg|png",
            "file_url": "",
            "filename": r"re:Perth.\(Kantai.Collection\).full.\d+",
            "height": r"re:^\d+$",
            "id": r"re:^\d+$",
            "name": "Perth (Kantai Collection)",
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
            thumbs = text.extract(page, '<ul id="thumbs', '</ul>')[0]
            extr = text.extract_from(thumbs)

            while True:
                post = extr('<li class="', '>')
                if not post:
                    break

                if metadata:
                    entry_id = extr('href="/', '"')
                    post = self._parse_entry_html(entry_id)
                    post.update(self._parse_entry_xml(entry_id))
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
            "author": "YukinoTokisaki",
            "date": "dt:2020-04-24 21:33:44",
            "file_url": str,
            "filename": "Perth.(Kantai.Collection).full.2920445",
            "height": "1366",
            "id": "2920445",
            "size": "1929k",
            "width": "1920",
        },
    })

    def __init__(self, match):
        ZerochanExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def posts(self):
        post = self._parse_entry_html(self.image_id)
        if self.config("metadata"):
            post.update(self._parse_entry_xml(self.image_id))
        return (post,)
