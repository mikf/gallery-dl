# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.newgrounds.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import itertools
import json


class NewgroundsExtractor(Extractor):
    """Base class for newgrounds extractors"""
    category = "newgrounds"
    directory_fmt = ("{category}", "{artist[:10]:J, }")
    filename_fmt = "{category}_{_index}_{title}.{extension}"
    archive_fmt = "{_index}"
    root = "https://www.newgrounds.com"
    cookiedomain = ".newgrounds.com"
    cookienames = ("NG_GG_username", "vmk1du5I8m")

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.user_root = "https://{}.newgrounds.com".format(self.user)

    def items(self):
        self.login()
        yield Message.Version, 1

        for post_url in self.posts():
            try:
                post = self.extract_post(post_url)
                url = post.get("url")
            except Exception:
                url = None

            if url:
                yield Message.Directory, post
                yield Message.Url, url, text.nameext_from_url(url, post)

                for num, url in enumerate(text.extract_iter(
                        post["_comment"], 'data-smartload-src="', '"'), 1):
                    post["num"] = num
                    post["_index"] = "{}_{:>02}".format(post["index"], num)
                    text.nameext_from_url(url, post)
                    yield Message.Url, url, post
            else:
                self.log.warning(
                    "Unable to get download URL for '%s'", post_url)

    def posts(self):
        """Return urls of all relevant image pages"""
        return self._pagination(self.subcategory)

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/passport/"
        page = self.request(url).text
        headers = {"Origin": self.root, "Referer": url}

        url = text.urljoin(self.root, text.extract(page, 'action="', '"')[0])
        data = {
            "username": username,
            "password": password,
            "remember": "1",
            "login"   : "1",
        }

        response = self.request(url, method="POST", headers=headers, data=data)
        if not response.history:
            raise exception.AuthenticationError()

        return {
            cookie.name: cookie.value
            for cookie in response.history[0].cookies
            if cookie.expires and cookie.domain == self.cookiedomain
        }

    def extract_post(self, post_url):
        response = self.request(post_url, fatal=False)
        if response.status_code >= 400:
            return {}
        page = response.text
        extr = text.extract_from(page)

        if "/art/view/" in post_url:
            data = self._extract_image_data(extr, post_url)
        elif "/audio/listen/" in post_url:
            data = self._extract_audio_data(extr, post_url)
        else:
            data = self._extract_media_data(extr, post_url)

        data["_comment"] = extr('id="author_comments"', '</div>')
        data["comment"] = text.unescape(text.remove_html(
            data["_comment"].partition(">")[2], "", ""))
        data["favorites"] = text.parse_int(extr(
            'id="faves_load">', '<').replace(",", ""))
        data["score"] = text.parse_float(extr('id="score_number">', '<'))
        data["tags"] = text.split_html(extr('<dd class="tags">', '</dd>'))
        data["artist"] = [
            text.extract(user, '//', '.')[0]
            for user in text.extract_iter(page, '<div class="item-user">', '>')
        ]

        data["tags"].sort()
        data["user"] = self.user or data["artist"][0]
        return data

    @staticmethod
    def _extract_image_data(extr, url):
        full = text.extract_from(json.loads(extr('"full_image_text":', '});')))
        data = {
            "title"      : text.unescape(extr('"og:title" content="', '"')),
            "description": text.unescape(extr(':description" content="', '"')),
            "date"       : text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"')),
            "rating"     : extr('class="rated-', '"'),
            "url"        : full('src="', '"'),
            "width"      : text.parse_int(full('width="', '"')),
            "height"     : text.parse_int(full('height="', '"')),
        }
        index = data["url"].rpartition("/")[2].partition("_")[0]
        data["index"] = text.parse_int(index)
        data["_index"] = index
        return data

    @staticmethod
    def _extract_audio_data(extr, url):
        index = url.split("/")[5]
        return {
            "title"      : text.unescape(extr('"og:title" content="', '"')),
            "description": text.unescape(extr(':description" content="', '"')),
            "date"       : text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"')),
            "url"        : extr('{"url":"', '"').replace("\\/", "/"),
            "index"      : text.parse_int(index),
            "_index"     : index,
            "rating"     : "",
        }

    def _extract_media_data(self, extr, url):
        index = url.split("/")[5]
        title = extr('"og:title" content="', '"')
        src = extr('{"url":"', '"')

        if src:
            src = src.replace("\\/", "/")
            date = text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"'))
        else:
            url = self.root + "/portal/video/" + index
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": self.root,
            }
            data = self.request(url, headers=headers).json()
            src = data["sources"]["360p"][0]["src"].replace(".360p.", ".")
            date = text.parse_timestamp(src.rpartition("?")[2])

        return {
            "title"      : text.unescape(title),
            "url"        : src,
            "date"       : date,
            "description": text.unescape(extr(
                'itemprop="description" content="', '"')),
            "rating"     : extr('class="rated-', '"'),
            "index"      : text.parse_int(index),
            "_index"     : index,
        }

    def _pagination(self, kind):
        root = self.user_root
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": root,
        }
        url = "{}/{}/page/1".format(root, kind)

        while True:
            with self.request(url, headers=headers, fatal=False) as response:
                try:
                    data = response.json()
                except ValueError:
                    return
                if not data:
                    return
                if "errors" in data:
                    msg = ", ".join(text.unescape(e) for e in data["errors"])
                    raise exception.StopExtraction(msg)

            for year in data["sequence"]:
                for item in data["years"][str(year)]["items"]:
                    page_url = text.extract(item, 'href="', '"')[0]
                    yield text.urljoin(root, page_url)

            if not data["more"]:
                return
            url = text.urljoin(root, data["more"])


class NewgroundsImageExtractor(NewgroundsExtractor):
    """Extractor for a single image from newgrounds.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:www\.)?newgrounds\.com/art/view/([^/?&#]+)/[^/?&#]+"
               r"|art\.ngfiles\.com/images/\d+/\d+_([^_]+)_([^.]+))")
    test = (
        ("https://www.newgrounds.com/art/view/tomfulp/ryu-is-hawt", {
            "url": "57f182bcbbf2612690c3a54f16ffa1da5105245e",
            "content": "8f395e08333eb2457ba8d8b715238f8910221365",
            "keyword": {
                "artist"     : ["tomfulp"],
                "comment"    : "re:Consider this the bottom threshold for ",
                "date"       : "dt:2009-06-04 14:44:05",
                "description": "re:Consider this the bottom threshold for ",
                "favorites"  : int,
                "filename"   : "94_tomfulp_ryu-is-hawt",
                "height"     : 476,
                "index"      : 94,
                "rating"     : "e",
                "score"      : float,
                "tags"       : ["ryu", "streetfighter"],
                "title"      : "Ryu is Hawt",
                "user"       : "tomfulp",
                "width"      : 447,
            },
        }),
        ("https://art.ngfiles.com/images/0/94_tomfulp_ryu-is-hawt.gif", {
            "url": "57f182bcbbf2612690c3a54f16ffa1da5105245e",
        }),
        ("https://www.newgrounds.com/art/view/sailoryon/yon-dream-buster", {
            "url": "84eec95e663041a80630df72719f231e157e5f5d",
            "count": 2,
        })
    )

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        if match.group(2):
            self.user = match.group(2)
            self.post_url = "https://www.newgrounds.com/art/view/{}/{}".format(
                self.user, match.group(3))
        else:
            self.post_url = text.ensure_http_scheme(match.group(0))

    def posts(self):
        return (self.post_url,)


class NewgroundsMediaExtractor(NewgroundsExtractor):
    """Extractor for a media file from newgrounds.com"""
    subcategory = "media"
    pattern = (r"(?:https?://)?(?:www\.)?newgrounds\.com"
               r"(/(?:portal/view|audio/listen)/\d+)")
    test = (
        ("https://www.newgrounds.com/portal/view/595355", {
            "pattern": r"https://uploads\.ungrounded\.net/alternate/564000"
                       r"/564957_alternate_31\.mp4\?1359712249",
            "keyword": {
                "artist"     : ["kickinthehead", "danpaladin", "tomfulp"],
                "comment"    : "re:My fan trailer for Alien Hominid HD!",
                "date"       : "dt:2013-02-01 09:50:49",
                "favorites"  : int,
                "filename"   : "564957_alternate_31",
                "index"      : 595355,
                "rating"     : "e",
                "score"      : float,
                "tags"       : ["alienhominid", "trailer"],
                "title"      : "Alien Hominid Fan Trailer",
                "user"       : "kickinthehead",
            },
        }),
        ("https://www.newgrounds.com/audio/listen/609768", {
            "url": "f4c5490ae559a3b05e46821bb7ee834f93a43c95",
            "keyword": {
                "artist"     : ["zj", "tomfulp"],
                "comment"    : "re:RECORDED 12-09-2014\n\nFrom The ZJ \"Late ",
                "date"       : "dt:2015-02-23 19:31:59",
                "description": "From The ZJ Report Show!",
                "favorites"  : int,
                "index"      : 609768,
                "rating"     : "",
                "score"      : float,
                "tags"       : ["fulp", "interview", "tom", "zj"],
                "title"      : "ZJ Interviews Tom Fulp!",
                "user"       : "zj",
            },
        }),
    )

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        self.user = ""
        self.post_url = self.root + match.group(1)

    def posts(self):
        return (self.post_url,)


class NewgroundsArtExtractor(NewgroundsExtractor):
    """Extractor for all images of a newgrounds user"""
    subcategory = "art"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/art/?$"
    test = ("https://tomfulp.newgrounds.com/art", {
        "pattern": NewgroundsImageExtractor.pattern,
        "count": ">= 3",
    })


class NewgroundsAudioExtractor(NewgroundsExtractor):
    """Extractor for all audio submissions of a newgrounds user"""
    subcategory = "audio"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/audio/?$"
    test = ("https://tomfulp.newgrounds.com/audio", {
        "pattern": r"https://audio.ngfiles.com/\d+/\d+_.+\.mp3",
        "count": ">= 4",
    })


class NewgroundsMoviesExtractor(NewgroundsExtractor):
    """Extractor for all movies of a newgrounds user"""
    subcategory = "movies"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/movies/?$"
    test = ("https://tomfulp.newgrounds.com/movies", {
        "pattern": r"https://uploads.ungrounded.net(/alternate)?/\d+/\d+_.+",
        "range": "1-10",
        "count": 10,
    })


class NewgroundsUserExtractor(NewgroundsExtractor):
    """Extractor for a newgrounds user profile"""
    subcategory = "user"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/?$"
    test = (
        ("https://tomfulp.newgrounds.com", {
            "pattern": "https://tomfulp.newgrounds.com/art$",
        }),
        ("https://tomfulp.newgrounds.com", {
            "options": (("include", "all"),),
            "pattern": "https://tomfulp.newgrounds.com/(art|audio|movies)$",
            "count": 3,
        }),
    )

    def items(self):
        base = self.user_root + "/"
        return self._dispatch_extractors((
            (NewgroundsArtExtractor   , base + "art"),
            (NewgroundsAudioExtractor , base + "audio"),
            (NewgroundsMoviesExtractor, base + "movies"),
        ), ("art",))


class NewgroundsFavoriteExtractor(NewgroundsExtractor):
    """Extractor for posts favorited by a newgrounds user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user}", "Favorites")
    pattern = (r"(?:https?://)?([^.]+)\.newgrounds\.com"
               r"/favorites(?!/following)(?:/(art|audio|movies))?/?")
    test = (
        ("https://tomfulp.newgrounds.com/favorites/art", {
            "range": "1-10",
            "count": ">= 10",
        }),
        ("https://tomfulp.newgrounds.com/favorites/audio"),
        ("https://tomfulp.newgrounds.com/favorites/movies"),
        ("https://tomfulp.newgrounds.com/favorites/"),
    )

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        self.kind = match.group(2)

    def posts(self):
        if self.kind:
            return self._pagination(self.kind)
        return itertools.chain.from_iterable(
            self._pagination(k) for k in ("art", "audio", "movies")
        )

    def _pagination(self, kind):
        num = 1
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.user_root,
        }

        while True:
            url = "{}/favorites/{}/{}".format(self.user_root, kind, num)
            response = self.request(url, headers=headers)
            if response.history:
                return

            favs = self._extract_favorites(response.text)
            yield from favs

            if len(favs) < 24:
                return
            num += 1

    def _extract_favorites(self, page):
        return [
            self.root + path
            for path in text.extract_iter(
                page, 'href="https://www.newgrounds.com', '"')
        ]


class NewgroundsFollowingExtractor(NewgroundsFavoriteExtractor):
    """Extractor for a newgrounds user's favorited users"""
    subcategory = "following"
    pattern = r"(?:https?://)?([^.]+)\.newgrounds\.com/favorites/(following)"
    test = ("https://tomfulp.newgrounds.com/favorites/following", {
        "pattern": NewgroundsUserExtractor.pattern,
        "range": "76-125",
        "count": 50,
    })

    def items(self):
        data = {"_extractor": NewgroundsUserExtractor}
        for url in self._pagination(self.kind):
            yield Message.Queue, url, data

    @staticmethod
    def _extract_favorites(page):
        return [
            text.ensure_http_scheme(user.rpartition('"')[2])
            for user in text.extract_iter(page, 'class="item-user', '"><img')
        ]
