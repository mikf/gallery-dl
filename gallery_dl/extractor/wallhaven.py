# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://alpha.wallhaven.cc/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache


class WallhavenExtractor(Extractor):
    """Base class for wallhaven extractors"""
    category = "wallhaven"
    filename_fmt = "{category}_{id}_{width}x{height}.{extension}"
    root = "https://alpha.wallhaven.cc"

    def login(self):
        """Login and set necessary cookies"""
        username, password = self._get_auth_info()
        if username:
            cookie = self._login_impl(username, password)
            self.session.cookies.set_cookie(cookie)

    @cache(maxage=365*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        self.log.info("Logging in as %s", username)

        url = "{}/auth/login".format(self.root)
        page = self.request(url).text
        pos = page.index('name="_token"')

        data = {
            "username": username,
            "password": password,
            "_token": text.extract(page, 'value="', '"', pos)[0]
        }
        response = self.request(
            url, method="POST", data=data, allow_redirects=False)

        for cookie in response.cookies:
            if cookie.name.startswith("remember_"):
                return cookie
        raise exception.AuthenticationError()

    def get_wallpaper_data(self, wallpaper_id):
        """Extract url and metadata for a wallpaper"""
        url = "{}/wallpaper/{}".format(self.root, wallpaper_id)
        page = self.request(url).text

        title, pos = text.extract(page, 'name="title" content="', '"')
        url, pos = text.extract(
            page, 'property="og:image" content="', '"', pos)
        resolution, pos = text.extract(
            page, '<h3 class="showcase-resolution"', '<', pos)
        colors  , pos = text.extract(page, '<ul ', '</ul>', pos)
        uploader, pos = text.extract(page, 'alt="', '"', pos)
        date    , pos = text.extract(page, 'datetime="', '"', pos)
        category, pos = text.extract(page, 'Category</dt><dd>', '<', pos)
        size    , pos = text.extract(page, 'Size</dt><dd>', '<', pos)
        views   , pos = text.extract(page, 'Views</dt><dd>', '<', pos)
        favs    , pos = text.extract(page, 'Favorites</dt><dd>', '</dt>', pos)

        width, _, height = resolution.rpartition(">")[2].partition("x")

        return text.urljoin(self.root, url), {
            "id": text.parse_int(wallpaper_id),
            "width": text.parse_int(width),
            "height": text.parse_int(height),
            "colors": list(text.extract_iter(colors, '#', '"')),
            "tags": title.rpartition(" | ")[0].lstrip("#").split(", #"),
            "uploader": text.unescape(uploader),
            "wh_category": category,
            "date": date,
            "size": size,
            "views": text.parse_int(views.replace(",", "")),
            "favorites": text.parse_int(
                text.remove_html(favs).partition(" ")[0]),
        }


class WallhavenSearchExtractor(WallhavenExtractor):
    """Extractor for search results on wallhaven.cc"""
    subcategory = "search"
    directory_fmt = ["{category}", "{search[q]}"]
    archive_fmt = "s_{search[q]}_{id}"
    pattern = [r"(?:https?://)?alpha\.wallhaven\.cc/search\?([^/?#]+)"]
    test = [
        ("https://alpha.wallhaven.cc/search?q=touhou", None),
        (("https://alpha.wallhaven.cc/search?q=id%3A87"
          "&categories=111&purity=100&sorting=relevance&order=desc&page=3"), {
            "url": "1b9b6d97b9670e32ef5dd6942a095549ab543d91",
            "range": "1-3",
        }),
    ]
    per_page = 24

    def __init__(self, match):
        WallhavenExtractor.__init__(self)
        self.params = text.parse_query(match.group(1))

    def items(self):
        self.login()
        yield Message.Version, 1
        yield Message.Directory, {"search": self.params}

        for wp_id in self.wallpapers():
            wp_url, wp_data = self.get_wallpaper_data(wp_id)
            wp_data["search"] = self.params
            yield Message.Url, wp_url, wp_data

    def wallpapers(self):
        """Yield wallpaper IDs from search results"""
        url = "{}/search".format(self.root)
        params = self.params.copy()
        headers = {
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
        }

        params["page"] = 1
        while True:
            page = self.request(url, params=params, headers=headers).text

            ids = list(text.extract_iter(page, 'data-wallpaper-id="', '"'))
            yield from ids

            if len(ids) < self.per_page:
                return
            params["page"] += 1


class WallhavenImageExtractor(WallhavenExtractor):
    """Extractor for individual wallpaper on wallhaven.cc"""
    subcategory = "image"
    archive_fmt = "{id}"
    pattern = [r"(?:https?://)?(?:alpha\.wallhaven\.cc/wallpaper"
               r"|whvn\.cc)/(\d+)"]
    test = [
        ("https://alpha.wallhaven.cc/wallpaper/8114", {
            "pattern": "https://[^.]+.wallhaven.cc/[^/]+/full/[^-]+-8114.jpg",
            "content": "497212679383a465da1e35bd75873240435085a2",
            "keyword": {
                "id": 8114,
                "width": 1920,
                "height": 1200,
                "colors": list,
                "tags": list,
                "uploader": "AksumkA",
                "date": "2014-08-31T06:17:19+00:00",
                "wh_category": "Anime",
                "size": "272.3 KiB",
                "views": int,
                "favorites": int,
            },
        }),
        # NSFW
        ("https://alpha.wallhaven.cc/wallpaper/8536", {
            "url": "8431c6f1eec3a6f113980eeec9dfcb707de7ddcf",
        }),
        ("https://whvn.cc/8114", None),
    ]

    def __init__(self, match):
        WallhavenExtractor.__init__(self)
        self.wallpaper_id = match.group(1)

    def items(self):
        self.login()
        url, data = self.get_wallpaper_data(self.wallpaper_id)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data
