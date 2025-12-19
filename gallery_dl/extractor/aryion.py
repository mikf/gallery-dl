# -*- coding: utf-8 -*-

# Copyright 2020-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://aryion.com/"""

from .common import Extractor, Message
from .. import text, util, dt, exception
from ..cache import cache
from email.utils import parsedate_tz

BASE_PATTERN = r"(?:https?://)?(?:www\.)?aryion\.com/g4"


class AryionExtractor(Extractor):
    """Base class for aryion extractors"""
    category = "aryion"
    directory_fmt = ("{category}", "{user!l}", "{path:I}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    cookies_domain = ".aryion.com"
    cookies_names = ("phpbb3_rl7a3_sid",)
    root = "https://aryion.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match[1]
        self.recursive = True

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=14*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/forum/ucp.php?mode=login"
        data = {
            "username": username,
            "password": password,
            "login": "Login",
        }

        response = self.request(url, method="POST", data=data)
        if b"You have been successfully logged in." not in response.content:
            raise exception.AuthenticationError()
        return {c: response.cookies[c] for c in self.cookies_names}

    def items(self):
        self.login()
        data = self.metadata()

        for post_id in self.posts():
            if post := self._parse_post(post_id):
                if data:
                    post.update(data)
                yield Message.Directory, "", post
                yield Message.Url, post["url"], post
            elif post is False and self.recursive:
                base = self.root + "/g4/view/"
                data = {"_extractor": AryionPostExtractor}
                for post_id in self._pagination_params(base + post_id):
                    yield Message.Queue, base + post_id, data

    def posts(self):
        """Yield relevant post IDs"""

    def metadata(self):
        """Return general metadata"""

    def _pagination_params(self, url, params=None, needle=None, quote="'"):
        if params is None:
            params = {"p": 1}
        else:
            params["p"] = text.parse_int(params.get("p"), 1)

        if needle is None:
            needle = "class='gallery-item' id=" + quote

        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for post_id in text.extract_iter(page, needle, quote):
                cnt += 1
                yield post_id

            if cnt < 40 and ">Next &gt;&gt;<" not in page:
                return
            params["p"] += 1

    def _pagination_next(self, url):
        while True:
            page = self.request(url).text
            yield from text.extract_iter(page, "thumb' href='/g4/view/", "'")

            pos = page.find("Next &gt;&gt;")
            if pos < 0:
                return
            url = self.root + text.rextr(page, "href='", "'", pos)

    def _pagination_folders(self, url, folder=None, seen=None):
        if folder is None:
            self.kwdict["folder"] = ""
        else:
            url = f"{url}/{folder}"
            self.kwdict["folder"] = folder = text.unquote(folder)
            self.log.debug("Descending into folder '%s'", folder)

        params = {"p": 1}
        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for item in text.extract_iter(
                    page, "<li class='gallery-item", "</li>"):
                cnt += 1
                if text.extr(item, 'data-item-type="', '"') == "Folders":
                    folder = text.extr(item, "href='", "'").rpartition("/")[2]
                    if seen is None:
                        seen = set()
                    if folder not in seen:
                        seen.add(folder)
                        if self.recursive:
                            yield from self._pagination_folders(
                                url, folder, seen)
                        else:
                            self.log.debug("Skipping folder '%s'", folder)
                else:
                    yield text.extr(item, "data-item-id='", "'")

            if cnt < 40 and ">Next &gt;&gt;<" not in page:
                break
            params["p"] += 1

        self.kwdict["folder"] = ""

    def _parse_post(self, post_id):
        url = f"{self.root}/g4/data.php?id={post_id}"
        with self.request(url, method="HEAD", fatal=False) as response:

            if response.status_code >= 400:
                self.log.warning(
                    "Unable to fetch post %s ('%s %s')",
                    post_id, response.status_code, response.reason)
                return None
            headers = response.headers

            # folder
            if headers["content-type"] in (
                "application/x-folder",
                "application/x-comic-folder",
                "application/x-comic-folder-nomerge",
            ):
                return False

            # get filename from 'Content-Disposition' header
            cdis = headers["content-disposition"]
            fname, _, ext = text.extr(cdis, 'filename="', '"').rpartition(".")
            if not fname:
                fname, ext = ext, fname

            # get file size from 'Content-Length' header
            clen = headers.get("content-length")

            # fix 'Last-Modified' header
            lmod = headers["last-modified"]
            if lmod[22] != ":":
                lmod = f"{lmod[:22]}:{lmod[22:24]} GMT"

        post_url = f"{self.root}/g4/view/{post_id}"
        extr = text.extract_from(self.request(post_url).text)

        title, _, artist = text.unescape(extr(
            "<title>g4 :: ", "<")).rpartition(" by ")

        return {
            "id"    : text.parse_int(post_id),
            "url"   : url,
            "user"  : self.user or artist,
            "title" : title,
            "artist": artist,
            "description": text.unescape(extr(
                'property="og:description" content="', '"')),
            "path"  : text.split_html(extr(
                "cookiecrumb'>", '</span'))[4:-1:2],
            "date"  : dt.datetime(*parsedate_tz(lmod)[:6]),
            "size"  : text.parse_int(clen),
            "views" : text.parse_int(extr("Views</b>:", "<").replace(",", "")),
            "width" : text.parse_int(extr("Resolution</b>:", "x")),
            "height": text.parse_int(extr("", "<")),
            "comments" : text.parse_int(extr("Comments</b>:", "<")),
            "favorites": text.parse_int(extr("Favorites</b>:", "<")),
            "tags"     : text.split_html(extr("class='taglist'>", "</span>")),
            "filename" : fname,
            "extension": ext,
            "_http_lastmodified": lmod,
        }


class AryionGalleryExtractor(AryionExtractor):
    """Extractor for a user's gallery on eka's portal"""
    subcategory = "gallery"
    categorytransfer = True
    pattern = rf"{BASE_PATTERN}/(?:gallery/|user/|latest.php\?name=)([^/?#]+)"
    example = "https://aryion.com/g4/gallery/USER"

    def _init(self):
        self.offset = 0
        self.recursive = self.config("recursive", True)

    def skip(self, num):
        if self.recursive:
            return 0
        self.offset += num
        return num

    def posts(self):
        if self.recursive:
            url = f"{self.root}/g4/gallery/{self.user}"
            return self._pagination_params(url)
        else:
            url = f"{self.root}/g4/latest.php?name={self.user}"
            return util.advance(self._pagination_next(url), self.offset)


class AryionFavoriteExtractor(AryionExtractor):
    """Extractor for a user's favorites gallery"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user!l}", "favorites", "{folder}")
    archive_fmt = "f_{user}_{id}"
    pattern = rf"{BASE_PATTERN}/favorites/([^/?#]+)(?:/([^?#]+))?"
    example = "https://aryion.com/g4/favorites/USER"

    def _init(self):
        self.recursive = self.config("recursive", True)

    def posts(self):
        url = f"{self.root}/g4/favorites/{self.user}"
        return self._pagination_folders(url, self.groups[1])


class AryionWatchExtractor(AryionExtractor):
    """Extractor for your watched users and tags"""
    subcategory = "watch"
    directory_fmt = ("{category}", "{user!l}",)
    pattern = rf"{BASE_PATTERN}/messagepage\.php()"
    example = "https://aryion.com/g4/messagepage.php"

    def posts(self):
        if not self.cookies_check(self.cookies_names):
            raise exception.AuthRequired(
                ("username & password", "authenticated cookies"),
                "watched Submissions")
        self.cookies.set("g4p_msgpage_style", "plain", domain="aryion.com")
        url = self.root + "/g4/messagepage.php"
        return self._pagination_params(url, None, 'data-item-id="', '"')


class AryionTagExtractor(AryionExtractor):
    """Extractor for tag searches on eka's portal"""
    subcategory = "tag"
    directory_fmt = ("{category}", "tags", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = rf"{BASE_PATTERN}/tags\.php\?([^#]+)"
    example = "https://aryion.com/g4/tags.php?tag=TAG"

    def _init(self):
        self.params = text.parse_query(self.user)
        self.user = None

    def metadata(self):
        return {"search_tags": self.params.get("tag")}

    def posts(self):
        url = self.root + "/g4/tags.php"
        return self._pagination_params(url, self.params)


class AryionSearchExtractor(AryionExtractor):
    """Extractor for searches on eka's portal"""
    subcategory = "search"
    directory_fmt = ("{category}", "searches", "{search[prefix]}"
                     "{search[q]|search[tags]|search[user]}")
    archive_fmt = ("s_{search[prefix]}"
                   "{search[q]|search[tags]|search[user]}_{id}")
    pattern = rf"{BASE_PATTERN}/search\.php\?([^#]+)"
    example = "https://aryion.com/g4/search.php?q=TEXT&tags=TAGS&user=USER"

    def metadata(self):
        params = text.parse_query(self.user)
        return {"search": {
            **params,
            "prefix": ("" if params.get("q") else
                       "t_" if params.get("tags") else
                       "u_" if params.get("user") else ""),
        }}

    def posts(self):
        url = f"{self.root}/g4/search.php?{self.user}"
        return self._pagination_next(url)


class AryionPostExtractor(AryionExtractor):
    """Extractor for individual posts on eka's portal"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/view/(\d+)"
    example = "https://aryion.com/g4/view/12345"

    def posts(self):
        post_id, self.user = self.user, None
        return (post_id,)
