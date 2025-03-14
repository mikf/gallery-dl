# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sankaku.app/"""

from .booru import BooruExtractor
from .common import Message
from .. import text, util, exception
from ..cache import cache
import collections
import re

BASE_PATTERN = r"(?:https?://)?" \
    r"(?:(?:chan|www|beta|black|white)\.sankakucomplex\.com|sankaku\.app)" \
    r"(?:/[a-z]{2})?"


class SankakuExtractor(BooruExtractor):
    """Base class for sankaku channel extractors"""
    basecategory = "booru"
    category = "sankaku"
    root = "https://sankaku.app"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    cookies_domain = None
    _warning = True

    TAG_TYPES = {
        0: "general",
        1: "artist",
        2: "studio",
        3: "copyright",
        4: "character",
        5: "genre",
        6: "",
        7: "",
        8: "medium",
        9: "meta",
    }

    def skip(self, num):
        return 0

    def _init(self):
        self.api = SankakuAPI(self)

    def _file_url(self, post):
        url = post["file_url"]
        if not url:
            if post["status"] != "active":
                self.log.warning(
                    "Unable to download post %s (%s)",
                    post["id"], post["status"])
            elif self._warning:
                self.log.warning(
                    "Login required to download 'contentious_content' posts")
                SankakuExtractor._warning = False
        elif url[8] == "v":
            url = "https://s.sankakucomplex.com" + url[url.index("/", 8):]
        return url

    def _prepare(self, post):
        post["created_at"] = post["created_at"]["s"]
        post["date"] = text.parse_timestamp(post["created_at"])
        post["tags"] = post.pop("tag_names", ())
        post["tag_string"] = " ".join(post["tags"])
        post["_http_validate"] = self._check_expired

    def _check_expired(self, response):
        return not response.history or '.com/expired.png' not in response.url

    def _tags(self, post, page):
        tags = collections.defaultdict(list)
        for tag in self.api.tags(post["id"]):
            name = tag["name"]
            if name:
                tags[tag["type"]].append(name.lower().replace(" ", "_"))
        types = self.TAG_TYPES
        for type, values in tags.items():
            name = types[type]
            post["tags_" + name] = values
            post["tag_string_" + name] = " ".join(values)

    def _notes(self, post, page):
        if post.get("has_notes"):
            post["notes"] = self.api.notes(post["id"])
            for note in post["notes"]:
                note["created_at"] = note["created_at"]["s"]
                note["updated_at"] = note["updated_at"]["s"]
        else:
            post["notes"] = ()


class SankakuTagExtractor(SankakuExtractor):
    """Extractor for images from sankaku.app by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"(?:/posts)?/?\?([^#]*)"
    example = "https://sankaku.app/?tags=TAG"

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        query = text.parse_query(match.group(1))
        self.tags = text.unquote(query.get("tags", "").replace("+", " "))

        if "date:" in self.tags:
            # rewrite 'date:' tags (#1790)
            self.tags = re.sub(
                r"date:(\d\d)[.-](\d\d)[.-](\d\d\d\d)(?!T)",
                r"date:\3-\2-\1T00:00", self.tags)
            self.tags = re.sub(
                r"date:(\d\d\d\d)[.-](\d\d)[.-](\d\d)(?!T)",
                r"date:\1-\2-\3T00:00", self.tags)

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        params = {"tags": self.tags}
        return self.api.posts_keyset(params)


class SankakuPoolExtractor(SankakuExtractor):
    """Extractor for image pools or books from sankaku.app"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name_en]}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/(?:books|pools?/show)/(\w+)"
    example = "https://sankaku.app/books/12345"

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.pool_id = match.group(1)

    def metadata(self):
        pool = self.api.pools(self.pool_id)
        pool["tags"] = [tag["name"] for tag in pool["tags"]]
        pool["artist_tags"] = [tag["name"] for tag in pool["artist_tags"]]

        self._posts = pool.pop("posts")
        for num, post in enumerate(self._posts, 1):
            post["num"] = num

        return {"pool": pool}

    def posts(self):
        return self._posts


class SankakuPostExtractor(SankakuExtractor):
    """Extractor for single posts from sankaku.app"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/posts?(?:/show)?/(\w+)"
    example = "https://sankaku.app/post/show/12345"

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return self.api.posts(self.post_id)


class SankakuBooksExtractor(SankakuExtractor):
    """Extractor for books by tag search on sankaku.app"""
    subcategory = "books"
    pattern = BASE_PATTERN + r"/books/?\?([^#]*)"
    example = "https://sankaku.app/books?tags=TAG"

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        query = text.parse_query(match.group(1))
        self.tags = text.unquote(query.get("tags", "").replace("+", " "))

    def items(self):
        params = {"tags": self.tags, "pool_type": "0"}
        for pool in self.api.pools_keyset(params):
            pool["_extractor"] = SankakuPoolExtractor
            url = "https://sankaku.app/books/{}".format(pool["id"])
            yield Message.Queue, url, pool


class SankakuAPI():
    """Interface for the sankaku.app API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Accept"     : "application/vnd.sankaku.api+json;v=2",
            "Api-Version": None,
            "Origin"     : extractor.root,
        }

        if extractor.config("id-format") in ("alnum", "alphanumeric"):
            self.headers["Api-Version"] = "2"

        self.username, self.password = extractor._get_auth_info()
        if not self.username:
            self.authenticate = util.noop

    def notes(self, post_id):
        params = {"lang": "en"}
        return self._call("/posts/{}/notes".format(post_id), params)

    def tags(self, post_id):
        endpoint = "/posts/{}/tags".format(post_id)
        params = {
            "lang" : "en",
            "page" : 1,
            "limit": 100,
        }

        tags = None
        while True:
            data = self._call(endpoint, params)

            tags_new = data["data"]
            if not tags_new:
                return tags or []
            elif tags is None:
                tags = tags_new
            else:
                tags.extend(tags_new)

            if len(tags_new) < 80 or len(tags) >= data["total"]:
                return tags
            params["page"] += 1

    def pools(self, pool_id):
        params = {"lang": "en"}
        return self._call("/pools/" + pool_id, params)

    def pools_keyset(self, params):
        return self._pagination("/pools/keyset", params)

    def pools_series(self, params):
        params_ = {
            "lang"       : "en",
            "filledPools": "true",
            "includes[]" : "pools",
        }
        params_.update(params)
        return self._pagination("/poolseriesv2", params)

    def posts(self, post_id):
        params = {
            "lang" : "en",
            "page" : "1",
            "limit": "1",
            "tags" : ("md5:" if len(post_id) == 32 else "id_range:") + post_id,
        }
        return self._call("/v2/posts", params)

    def posts_keyset(self, params):
        return self._pagination("/v2/posts/keyset", params)

    def authenticate(self):
        self.headers["Authorization"] = \
            _authenticate_impl(self.extractor, self.username, self.password)

    def _call(self, endpoint, params=None):
        url = "https://sankakuapi.com" + endpoint
        for _ in range(5):
            self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code == 429:
                until = response.headers.get("X-RateLimit-Reset")
                if not until and b"_tags-explicit-limit" in response.content:
                    raise exception.AuthorizationError(
                        "Search tag limit exceeded")
                seconds = None if until else 600
                self.extractor.wait(until=until, seconds=seconds)
                continue

            data = response.json()
            try:
                success = data.get("success", True)
            except AttributeError:
                success = True
            if not success:
                code = data.get("code")
                if code and code.endswith(
                        ("unauthorized", "invalid-token", "invalid_token")):
                    _authenticate_impl.invalidate(self.username)
                    continue
                raise exception.StopExtraction(code)
            return data

    def _pagination(self, endpoint, params):
        params["lang"] = "en"
        params["limit"] = str(self.extractor.per_page)

        refresh = self.extractor.config("refresh", False)
        if refresh:
            offset = expires = 0
            from time import time

        while True:
            data = self._call(endpoint, params)

            if refresh:
                posts = data["data"]
                if offset:
                    posts = util.advance(posts, offset)

                for post in posts:
                    if not expires:
                        url = post["file_url"]
                        if url:
                            expires = text.parse_int(
                                text.extr(url, "e=", "&")) - 60

                    if 0 < expires <= time():
                        self.extractor.log.debug("Refreshing download URLs")
                        expires = None
                        break

                    offset += 1
                    yield post

                if expires is None:
                    expires = 0
                    continue
                offset = expires = 0

            else:
                yield from data["data"]

            params["next"] = data["meta"]["next"]
            if not params["next"]:
                return


@cache(maxage=365*86400, keyarg=1)
def _authenticate_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    url = "https://sankakuapi.com/auth/token"
    headers = {"Accept": "application/vnd.sankaku.api+json;v=2"}
    data = {"login": username, "password": password}

    response = extr.request(
        url, method="POST", headers=headers, json=data, fatal=False)
    data = response.json()

    if response.status_code >= 400 or not data.get("success"):
        raise exception.AuthenticationError(data.get("error"))
    return "Bearer " + data["access_token"]
