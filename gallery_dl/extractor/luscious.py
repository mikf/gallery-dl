# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://luscious.net/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception
from ..cache import cache


class LusciousBase(Extractor):
    """Base class for luscious extractors"""
    category = "luscious"
    cookiedomain = ".luscious.net"
    root = "https://members.luscious.net"

    def login(self):
        """Login and set necessary cookies"""
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=14*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)
        url = "https://members.luscious.net/accounts/login/"
        headers = {"Referer": "https://members.luscious.net/login/"}
        data = {
            "login": username,
            "password": password,
            "remember": "on",
            "next": "/",
        }

        response = self.request(url, method="POST", headers=headers, data=data)
        if "/accounts/login/" in response.url or not response.history:
            raise exception.AuthenticationError()
        for cookie in response.history[0].cookies:
            if cookie.name.startswith("sessionid_"):
                return {cookie.name: cookie.value}
        raise exception.AuthenticationError()

    @staticmethod
    def _parse_tags(tags):
        return [
            text.unescape(tag.replace(":_", ":"))
            for tag in text.extract_iter(tags or "", "/tags/", "/")
        ]


class LusciousAlbumExtractor(LusciousBase, GalleryExtractor):
    """Extractor for image albums from luscious.net"""
    subcategory = "album"
    archive_fmt = "{gallery_id}_{image_id}"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/(?:albums|pictures/c/[^/?&#]+/album)/([^/?&#]+_(\d+))")
    test = (
        ("https://luscious.net/albums/okinami-no-koigokoro_277031/", {
            "url": "7e4984a271a1072ac6483e4228a045895aff86f3",
            "keyword": "c597c132834f4990f90bf5dee5de2a9d4ba263a4",
            "content": "b3a747a6464509440bd0ff6d1267e6959f8d6ff3",
        }),
        ("https://luscious.net/albums/virgin-killer-sweater_282582/", {
            "url": "21cc68a7548f4d71dfd67d8caf96349dde7e791c",
            "keyword": "e1202078b504adeccd521aa932f456a5a85479a0",
        }),
        ("https://luscious.net/albums/not-found_277035/", {
            "exception": exception.NotFoundError,
        }),
        ("https://members.luscious.net/albums/login-required_323871/", {
            "options": (("username", None),),
            "exception": exception.AuthorizationError,
        }),
        ("https://www.luscious.net/albums/okinami_277031/"),
        ("https://members.luscious.net/albums/okinami_277031/"),
        ("https://luscious.net/pictures/c/video_game_manga/album"
         "/okinami-no-koigokoro_277031/sorted/position/id/16528978/@_1"),
    )

    def __init__(self, match):
        path, self.gallery_id = match.groups()
        url = "{}/albums/{}/".format(self.root, path)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        pos = page.find("<h1>404 Not Found</h1>")
        if pos >= 0:
            msg = text.extract(page, '<div class="content">', '</div>', pos)[0]
            if msg and "content is not available" in msg:
                raise exception.AuthorizationError()
            raise exception.NotFoundError("album")

        title, pos = text.extract(page, '"og:title" content="', '"')
        info , pos = text.extract(page, '<li class="user_info">', "", pos)
        if info is None:
            count, pos = text.extract(page, '>Pages:', '<', pos)
        else:
            count, pos = text.extract(page, '<p>', ' ', pos)
        genre, pos = text.extract(page, '<p>Genre:', '</p>', pos)
        adnce, pos = text.extract(page, '<p>Audience:', '</p>', pos)
        tags , pos = text.extract(page, '"tag_list static">', '</ol>', pos)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(title or ""),
            "count"     : text.parse_int(count),
            "genre"     : text.remove_html(genre),
            "audience"  : text.remove_html(adnce),
            "tags"      : self._parse_tags(tags),
        }

    def images(self, page):
        extr = text.extract

        url = "{}/pictures/album/x_{}/sorted/old/page/1/".format(
            self.root, self.gallery_id)
        page = self.request(url).text
        pos = page.find('<div id="picture_page_')
        url = extr(page, '<a href="', '"', pos)[0]
        iurl = None

        while url and not url.endswith("/more_like_this/"):
            page = self.request(self.root + url).text

            if not iurl:  # first loop iteraton
                current = extr(page, '"pj_current_page" value="', '"')[0]
                if current and current != "1":
                    url = "{}/albums/{}/jump_to_page/1/".format(
                        self.root, self.gallery_id)
                    page = self.request(url, method="POST").text

            iid , pos = extr(url , '/id/', '/')
            url , pos = extr(page, '<link rel="next" href="', '"')
            name, pos = extr(page, '<h1 id="picture_title">', '</h1>', pos)
            _   , pos = extr(page, '<ul class="image_option_icons">', '', pos)
            iurl, pos = extr(page, '<li><a href="', '"', pos+100)

            if iurl[0] == "/":
                iurl = text.urljoin(self.root, iurl)

            yield iurl, {
                "name": name,
                "image_id": text.parse_int(iid),
            }


class LusciousSearchExtractor(LusciousBase, Extractor):
    """Extractor for album searches on luscious.net"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/(albums(?:/(?![^/?&#]+_\d+)[^/?&#]+)+|manga|pictures)/?$")
    test = (
        ("https://luscious.net/manga/"),
        ("https://members.luscious.net/albums/sorted/updated/album_type/manga"
         "/content_id/2/tagged/+full_color/page/1/", {
             "pattern": LusciousAlbumExtractor.pattern,
             "range": "20-40",
             "count": 21,
         }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1).partition("/page/")[0]
        if not self.path.startswith("albums/"):
            self.path = "albums/sorted/updated/album_type/" + self.path

    def items(self):
        self.login()
        yield Message.Version, 1
        for album in self.albums():
            url, data = self.parse_album(album)
            yield Message.Queue, url, data

    def albums(self, pnum=1):
        while True:
            url = "{}/{}/page/{}/.json/".format(self.root, self.path, pnum)
            data = self.request(url).json()

            yield from text.extract_iter(
                data["html"], "<figcaption>", "</figcaption>")

            if data["paginator_complete"]:
                return
            pnum += 1

    def parse_album(self, album):
        url  , pos = text.extract(album, 'href="', '"')
        title, pos = text.extract(album, ">", "<", pos)
        count, pos = text.extract(album, "# of pictures:", "<", pos)
        date , pos = text.extract(album, "Updated:&nbsp;", "<", pos)
        desc , pos = text.extract(album, "class='desc'>", "<", pos)
        tags , pos = text.extract(album, "<ol ", "</ol>", pos)

        return text.urljoin(self.root, url), {
            "title": text.unescape(title or ""),
            "description": text.unescape(desc or ""),
            "gallery_id": text.parse_int(url.rpartition("_")[2].rstrip("/")),
            "count": text.parse_int(count),
            "date": date,
            "tags": self._parse_tags(tags),
            "_extractor": LusciousAlbumExtractor,
        }
