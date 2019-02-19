# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://luscious.net/"""

from .common import Extractor, Message, AsynchronousMixin
from .. import text, util, exception
from ..cache import cache


class LusciousExtractor(Extractor):
    """Base class for luscious extractors"""
    category = "luscious"
    cookiedomain = ".luscious.net"
    root = "https://members.luscious.net"

    def login(self):
        """Login and set necessary cookies"""
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=14*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)
        url = "https://members.luscious.net/accounts/login/"
        headers = {"Referer": "https://members.luscious.net/login/"}
        data = {
            "login": username,
            "password": password,
            "remember": "on",
            "next": ""  "/",
        }

        response = self.request(url, method="POST", headers=headers, data=data)
        if "/accounts/login/" in response.url or not response.history:
            raise exception.AuthenticationError()
        for cookie in response.history[0].cookies:
            if cookie.name.startswith("sessionid_"):
                return {cookie.name: cookie.value}
        raise exception.AuthenticationError()


class LusciousAlbumExtractor(AsynchronousMixin, LusciousExtractor):
    """Extractor for image albums from luscious.net"""
    subcategory = "album"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    archive_fmt = "{gallery_id}_{image_id}"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/(?:albums|pictures/c/[^/?&#]+/album)/([^/?&#]+_(\d+))")
    test = (
        ("https://luscious.net/albums/okinami-no-koigokoro_277031/", {
            "url": "7e4984a271a1072ac6483e4228a045895aff86f3",
            "keyword": "5ab53959f25a468455f79149461d26547669e50e",
            "content": "b3a747a6464509440bd0ff6d1267e6959f8d6ff3",
        }),
        ("https://luscious.net/albums/virgin-killer-sweater_282582/", {
            "url": "21cc68a7548f4d71dfd67d8caf96349dde7e791c",
            "keyword": "3de82f61ad4afd0f546ab5ae5bf9c5388cc9c3db",
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
        LusciousExtractor.__init__(self, match)
        self.gpart, self.gid = match.groups()

    def items(self):
        self.login()
        url = "{}/albums/{}/".format(self.root, self.gpart)
        page = self.request(url).text
        data = self.metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.images(page):
            image.update(data)
            yield Message.Url, url, image

    def metadata(self, page):
        """Collect metadata for extractor-job"""
        pos = page.find("<h1>404 Not Found</h1>")
        if pos >= 0:
            msg = text.extract(page, '<div class="content">', '</div>', pos)[0]
            if msg and "content is not available" in msg:
                raise exception.AuthorizationError()
            raise exception.NotFoundError("album")

        data = text.extract_all(page, (
            ("tags"    , '<meta name="keywords" content="', '"'),
            ("title"   , '"og:title" content="', '"'),
            (None      , '<li class="user_info">', ''),
            ("count"   , '<p>', ' '),
            (None      , '<p>Section:', ''),
            ("section" , '>', '<'),
            ("language", '<p>Language:', ' '),
        ), values={"gallery_id": self.gid})[0]
        data["lang"] = util.language_to_code(data["language"])
        try:
            data["artist"] = text.extract(data["tags"], "rtist: ", ",")[0]
        except AttributeError:
            data["artist"] = None
        return data

    def images(self, page):
        """Collect image-URLs and -metadata"""
        extr = text.extract
        num = 1

        if 'class="search_filter' in page:
            url = "{}/pictures/album/x_{}/sorted/oldest/page/1/".format(
                self.root, self.gid)
            page = self.request(url).text
            pos = page.find('<div id="picture_page_')
        else:
            pos = page.find('<div class="album_cover_item">')
        url = extr(page, '<a href="', '"', pos)[0]

        while url and not url.endswith("/more_like_this/"):
            page = self.request(self.root + url).text

            if num == 1:
                current = extr(page, '"pj_current_page" value="', '"')[0]
                if current and current != "1":
                    url = "{}/albums/{}/jump_to_page/1/".format(
                        self.root, self.gid)
                    page = self.request(url, method="POST").text

            imgid, pos = extr(url , '/id/', '/')
            url  , pos = extr(page, '<link rel="next" href="', '"')
            name , pos = extr(page, '<h1 id="picture_title">', '</h1>', pos)
            _    , pos = extr(page, '<ul class="image_option_icons">', '', pos)
            iurl , pos = extr(page, '<li><a href="', '"', pos+100)

            if iurl[0] == "/":
                iurl = text.urljoin(self.root, iurl)

            yield iurl, {
                "num": num,
                "name": name,
                "extension": iurl.rpartition(".")[2],
                "image_id": imgid,
            }
            num += 1


class LusciousSearchExtractor(LusciousExtractor):
    """Extractor for album searches on luscious.net"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/((?:albums|c)(?:/(?![^/?&#]+_\d+)[^/?&#]+)+)")
    test = (
        ("https://luscious.net/c/hentai/"),
        ("https://luscious.net/albums/t2/2/c/hentai/sorted/updated"
         "/tagged/+full_color/page/2/", {
             "pattern": r"https://(members\.)?luscious.net/albums/[^_]+_\d+/",
             "range": "20-40",
             "count": 21,
         }),
    )

    def __init__(self, match):
        LusciousExtractor.__init__(self, match)
        self.path = match.group(1).partition("/page/")[0]
        if not self.path.startswith("albums/"):
            self.path = "albums/" + self.path

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
            "gallery_id": url.rpartition("_")[2].rstrip("/"),
            "count": text.parse_int(count),
            "date": date,
            "tags": text.remove_html(tags.partition(">")[2]),
            "_extractor": LusciousAlbumExtractor,
        }
