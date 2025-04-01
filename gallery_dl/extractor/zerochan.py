# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.zerochan.net/"""

from .booru import BooruExtractor
from ..cache import cache
from .. import text, util, exception
import collections
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?zerochan\.net"


class ZerochanExtractor(BooruExtractor):
    """Base class for zerochan extractors"""
    category = "zerochan"
    root = "https://www.zerochan.net"
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    page_start = 1
    per_page = 250
    cookies_domain = ".zerochan.net"
    cookies_names = ("z_id", "z_hash")
    request_interval = (0.5, 1.5)

    def login(self):
        self._logged_in = True
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

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
        page = self.request(url).text

        try:
            jsonld = self._extract_jsonld(page)
        except Exception:
            return {"id": entry_id}

        extr = text.extract_from(page)
        data = {
            "id"      : text.parse_int(entry_id),
            "file_url": jsonld["contentUrl"],
            "date"    : text.parse_datetime(jsonld["datePublished"]),
            "width"   : text.parse_int(jsonld["width"][:-3]),
            "height"  : text.parse_int(jsonld["height"][:-3]),
            "size"    : text.parse_bytes(jsonld["contentSize"][:-1]),
            "path"    : text.split_html(extr(
                'class="breadcrumbs', '</nav>'))[2:],
            "uploader": extr('href="/user/', '"'),
            "tags"    : extr('<ul id="tags"', '</ul>'),
            "source"  : text.unescape(text.remove_html(extr(
                'id="source-url"', '</p>').rpartition("</s>")[2])),
        }

        try:
            data["author"] = jsonld["author"]["name"]
        except Exception:
            data["author"] = ""

        html = data["tags"]
        tags = data["tags"] = []
        for tag in html.split("<li class=")[1:]:
            category = text.extr(tag, '"', '"')
            name = text.unescape(text.extr(tag, 'data-tag="', '"'))
            tags.append(category.partition(" ")[0].capitalize() + ":" + name)

        return data

    def _parse_entry_api(self, entry_id):
        url = "{}/{}?json".format(self.root, entry_id)
        txt = self.request(url).text
        try:
            item = util.json_loads(txt)
        except ValueError:
            item = self._parse_json(txt)
            item["id"] = text.parse_int(entry_id)

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

    def _parse_json(self, txt):
        txt = re.sub(r"[\x00-\x1f\x7f]", "", txt)
        main, _, tags = txt.partition('tags": [')

        item = {}
        for line in main.split(',  "')[1:]:
            key, _, value = line.partition('": ')
            if value:
                if value[0] == '"':
                    value = value[1:-1]
                else:
                    value = text.parse_int(value)
            if key:
                item[key] = value

        item["tags"] = tags = tags[5:].split('",    "')
        if tags:
            tags[-1] = tags[-1][:-5]

        return item

    def _tags(self, post, page):
        tags = collections.defaultdict(list)
        for tag in post["tags"]:
            category, _, name = tag.partition(":")
            tags[category].append(name)
        for key, value in tags.items():
            post["tags_" + key.lower()] = value


class ZerochanTagExtractor(ZerochanExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"/(?!\d+$)([^/?#]+)/?(?:\?([^#]+))?"
    example = "https://www.zerochan.net/TAG"

    def __init__(self, match):
        ZerochanExtractor.__init__(self, match)
        self.search_tag, self.query = match.groups()

    def _init(self):
        if self.config("pagination") == "html":
            self.posts = self.posts_html
            self.per_page = 24
        else:
            self.posts = self.posts_api
            self.session.headers["User-Agent"] = util.USERAGENT

        exts = self.config("extensions")
        if exts:
            if isinstance(exts, str):
                exts = exts.split(",")
            self.exts = exts
        else:
            self.exts = ("jpg", "png", "webp", "gif")

    def metadata(self):
        return {"search_tags": text.unquote(
            self.search_tag.replace("+", " "))}

    def posts_html(self):
        url = self.root + "/" + self.search_tag
        params = text.parse_query(self.query)
        params["p"] = text.parse_int(params.get("p"), self.page_start)
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
                    post.update(self._parse_entry_api(entry_id))
                    yield post
                else:
                    yield {
                        "id"    : extr('href="/', '"'),
                        "name"  : extr('alt="', '"'),
                        "width" : extr('title="', '&#10005;'),
                        "height": extr('', ' '),
                        "size"  : extr('', 'b'),
                        "file_url": "https://static." + extr(
                            '<a href="https://static.', '"'),
                    }

            if 'rel="next"' not in page:
                break
            params["p"] += 1

    def posts_api(self):
        url = self.root + "/" + self.search_tag
        metadata = self.config("metadata")
        params = {
            "json": "1",
            "l"   : self.per_page,
            "p"   : self.page_start,
        }

        while True:
            response = self.request(url, params=params, allow_redirects=False)

            if response.status_code >= 300:
                url = text.urljoin(self.root, response.headers["location"])
                self.log.warning("HTTP redirect to %s", url)
                if self.config("redirects"):
                    continue
                raise exception.StopExtraction()

            data = response.json()
            try:
                posts = data["items"]
            except Exception:
                self.log.debug("Server response: %s", data)
                return

            if metadata:
                for post in posts:
                    post_id = post["id"]
                    post.update(self._parse_entry_html(post_id))
                    post.update(self._parse_entry_api(post_id))
                    yield post
            else:
                for post in posts:
                    urls = self._urls(post)
                    post["file_url"] = next(urls)
                    post["_fallback"] = urls
                    yield post

            if not data.get("next"):
                return
            params["p"] += 1

    def _urls(self, post, static="https://static.zerochan.net/.full."):
        base = static + str(post["id"]) + "."
        for ext in self.exts:
            yield base + ext


class ZerochanImageExtractor(ZerochanExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/(\d+)"
    example = "https://www.zerochan.net/12345"

    def __init__(self, match):
        ZerochanExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def posts(self):
        post = self._parse_entry_html(self.image_id)
        if self.config("metadata"):
            post.update(self._parse_entry_api(self.image_id))
        return (post,)
