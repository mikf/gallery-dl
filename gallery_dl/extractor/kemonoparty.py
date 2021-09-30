# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kemono.party/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import itertools
import re

BASE_PATTERN = r"(?:https?://)?kemono\.party/([^/?#]+)/user/([^/?#]+)"


class KemonopartyExtractor(Extractor):
    """Base class for kemonoparty extractors"""
    category = "kemonoparty"
    root = "https://kemono.party"
    directory_fmt = ("{category}", "{service}", "{user}")
    filename_fmt = "{id}_{title}_{num:>02}_{filename}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"
    cookiedomain = ".kemono.party"

    def items(self):
        self._prepare_ddosguard_cookies()

        find_inline = re.compile(r'src="(/inline/[^"]+)').findall
        skip_service = \
            "patreon" if self.config("patreon-skip-file", True) else None

        if self.config("metadata"):
            username = text.unescape(text.extract(
                self.request(self.user_url).text,
                '<meta name="artist_name" content="', '"')[0])
        else:
            username = None

        posts = self.posts()
        max_posts = self.config("max-posts")
        if max_posts:
            posts = itertools.islice(posts, max_posts)

        for post in posts:

            files = []
            append = files.append
            file = post["file"]

            if file:
                file["type"] = "file"
                if post["service"] != skip_service or not post["attachments"]:
                    append(file)
            for attachment in post["attachments"]:
                attachment["type"] = "attachment"
                append(attachment)
            for path in find_inline(post["content"] or ""):
                append({"path": path, "name": path, "type": "inline"})

            post["date"] = text.parse_datetime(
                post["published"], "%a, %d %b %Y %H:%M:%S %Z")
            if username:
                post["username"] = username
            yield Message.Directory, post

            for post["num"], file in enumerate(files, 1):
                post["type"] = file["type"]
                url = file["path"]
                if url[0] == "/":
                    url = self.root + "/data" + url
                elif url.startswith("https://kemono.party"):
                    url = self.root + "/data" + url[20:]

                text.nameext_from_url(file["name"], post)
                yield Message.Url, url, post

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=28*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/account/login"
        data = {"username": username, "password": password}

        response = self.request(url, method="POST", data=data)
        if response.url.endswith("/account/login") and \
                "Username or password is incorrect" in response.text:
            raise exception.AuthenticationError()

        return {c.name: c.value for c in response.history[0].cookies}


class KemonopartyUserExtractor(KemonopartyExtractor):
    """Extractor for all posts from a kemono.party user listing"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/?(?:\?o=(\d+))?(?:$|[?#])"
    test = (
        ("https://kemono.party/fanbox/user/6993449", {
            "range": "1-25",
            "count": 25,
        }),
        # 'max-posts' option, 'o' query parameter (#1674)
        ("https://kemono.party/patreon/user/881792?o=150", {
            "options": (("max-posts", 25),),
            "count": "< 100",
        }),
        ("https://kemono.party/subscribestar/user/alcorart"),
    )

    def __init__(self, match):
        KemonopartyExtractor.__init__(self, match)
        service, user_id, offset = match.groups()
        self.api_url = "{}/api/{}/user/{}".format(self.root, service, user_id)
        self.user_url = "{}/{}/user/{}".format(self.root, service, user_id)
        self.offset = text.parse_int(offset)

    def posts(self):
        url = self.api_url
        params = {"o": self.offset}

        while True:
            posts = self.request(url, params=params).json()
            yield from posts

            if len(posts) < 25:
                return
            params["o"] += 25


class KemonopartyPostExtractor(KemonopartyExtractor):
    """Extractor for a single kemono.party post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/post/([^/?#]+)"
    test = (
        ("https://kemono.party/fanbox/user/6993449/post/506575", {
            "pattern": r"https://kemono\.party/data/files/fanbox"
                       r"/6993449/506575/P058kDFYus7DbqAkGlfWTlOr\.jpeg",
            "keyword": {
                "added": "Wed, 06 May 2020 20:28:02 GMT",
                "content": str,
                "date": "dt:2019-08-11 02:09:04",
                "edited": None,
                "embed": dict,
                "extension": "jpeg",
                "filename": "P058kDFYus7DbqAkGlfWTlOr",
                "id": "506575",
                "num": 1,
                "published": "Sun, 11 Aug 2019 02:09:04 GMT",
                "service": "fanbox",
                "shared_file": False,
                "subcategory": "post",
                "title": "c96取り置き",
                "type": "file",
                "user": "6993449",
            },
        }),
        # inline image (#1286)
        ("https://kemono.party/fanbox/user/7356311/post/802343", {
            "pattern": r"https://kemono\.party/data/inline/fanbox"
                       r"/uaozO4Yga6ydkGIJFAQDixfE\.jpeg",
        }),
        # kemono.party -> data.kemono.party
        ("https://kemono.party/gumroad/user/trylsc/post/IURjT", {
            "pattern": r"https://kemono\.party/data/(file|attachment)s"
                       r"/gumroad/trylsc/IURjT/",
        }),
        # username (#1548, #1652)
        ("https://kemono.party/gumroad/user/3252870377455/post/aJnAH", {
            "options": (("metadata", True),),
            "keyword": {"username": "Kudalyn's Creations"},
        }),
        # skip patreon main file (#1667, #1689)
        ("https://kemono.party/patreon/user/4158582/post/32099982", {
            "count": 2,
            "keyword": {"type": "attachment"},
        }),
        ("https://kemono.party/subscribestar/user/alcorart/post/184330"),
    )

    def __init__(self, match):
        KemonopartyExtractor.__init__(self, match)
        service, user_id, post_id = match.groups()
        self.api_url = "{}/api/{}/user/{}/post/{}".format(
            self.root, service, user_id, post_id)
        self.user_url = "{}/{}/user/{}".format(self.root, service, user_id)

    def posts(self):
        posts = self.request(self.api_url).json()
        return (posts[0],) if len(posts) > 1 else posts


class KemonopartyFavoriteExtractor(KemonopartyExtractor):
    """Extractor for kemono.party favorites"""
    subcategory = "favorite"
    pattern = r"(?:https?://)?kemono\.party/favorites"
    test = ("https://kemono.party/favorites", {
        "pattern": KemonopartyUserExtractor.pattern,
        "url": "f4b5b796979bcba824af84206578c79101c7f0e1",
        "count": 3,
    })

    def items(self):
        self._prepare_ddosguard_cookies()
        self.login()

        users = self.request(self.root + "/api/favorites").json()
        for user in users:
            user["_extractor"] = KemonopartyUserExtractor
            url = "{}/{}/user/{}".format(
                self.root, user["service"], user["id"])
            yield Message.Queue, url, user
