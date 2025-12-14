# -*- coding: utf-8 -*-

# Copyright 2014-2025 Mike Fährmann
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

BASE_PATTERN = r"(?:https?://)?" \
    r"(?:(?:chan|www|beta|black|white)\.sankakucomplex\.com|sankaku\.app)" \
    r"(?:/[a-z]{2}(?:[-_][A-Z]{2})?)?"


class SankakuExtractor(BooruExtractor):
    """Base class for sankaku channel extractors"""
    basecategory = "booru"
    category = "sankaku"
    root = "https://sankaku.app"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
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
        if self.config("tags") == "extended":
            self._tags = self._tags_extended
            self._tags_findall = text.re(
                r"tag-type-([^\"' ]+).*?\?tags=([^\"'&]+)").findall

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
        elif url[4] != "s":
            url = "https" + url[4:]
        return url

    def _prepare(self, post):
        post["created_at"] = post["created_at"]["s"]
        post["date"] = self.parse_timestamp(post["created_at"])
        post["tags"] = post.pop("tag_names", ())
        post["tag_string"] = " ".join(post["tags"])
        post["_http_validate"] = self._check_expired

    def _check_expired(self, response):
        return not response.history or '.com/expired.png' not in response.url

    def _tags(self, post, page):
        tags = collections.defaultdict(list)
        for tag in self.api.tags(post["id"]):
            if name := tag["name"]:
                tags[tag["type"]].append(name.lower().replace(" ", "_"))
        types = self.TAG_TYPES
        for type, values in tags.items():
            name = types[type]
            post["tags_" + name] = values
            post["tag_string_" + name] = " ".join(values)

    def _tags_extended(self, post, page):
        try:
            url = "https://chan.sankakucomplex.com/posts/" + post["id"]
            headers = {"Referer": url}
            page = self.request(url, headers=headers).text
        except Exception as exc:
            return self.log.warning(
                "%s: Failed to extract extended tag categories (%s: %s)",
                post["id"], exc.__class__.__name__, exc)

        tags = collections.defaultdict(list)
        tag_sidebar = text.extr(page, '<ul id="tag-sidebar"', "</ul>")
        for tag_type, tag_name in self._tags_findall(tag_sidebar):
            tags[tag_type].append(text.unescape(text.unquote(tag_name)))
        for type, values in tags.items():
            post["tags_" + type] = values
            post["tag_string_" + type] = " ".join(values)

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
    pattern = rf"{BASE_PATTERN}(?:/posts)?/?\?([^#]*)"
    example = "https://sankaku.app/?tags=TAG"

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        query = text.parse_query(match[1])
        self.tags = text.unquote(query.get("tags", "").replace("+", " "))

        if "date:" in self.tags:
            # rewrite 'date:' tags (#1790)
            self.tags = text.re(
                r"date:(\d\d)[.-](\d\d)[.-](\d\d\d\d)(?!T)").sub(
                r"date:\3-\2-\1T00:00", self.tags)
            self.tags = text.re(
                r"date:(\d\d\d\d)[.-](\d\d)[.-](\d\d)(?!T)").sub(
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
    pattern = rf"{BASE_PATTERN}/(?:books|pools?/show)/(\w+)"
    example = "https://sankaku.app/books/12345"

    def metadata(self):
        pool = self.api.pools(self.groups[0])
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
    pattern = rf"{BASE_PATTERN}/posts?(?:/show)?/(\w+)"
    example = "https://sankaku.app/post/show/12345"

    def posts(self):
        return self.api.posts(self.groups[0])


class SankakuBooksExtractor(SankakuExtractor):
    """Extractor for books by tag search on sankaku.app"""
    subcategory = "books"
    pattern = rf"{BASE_PATTERN}/books/?\?([^#]*)"
    example = "https://sankaku.app/books?tags=TAG"

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        query = text.parse_query(match[1])
        self.tags = text.unquote(query.get("tags", "").replace("+", " "))

    def items(self):
        params = {"tags": self.tags, "pool_type": "0"}
        for pool in self.api.pools_keyset(params):
            pool["_extractor"] = SankakuPoolExtractor
            url = f"https://sankaku.app/books/{pool['id']}"
            yield Message.Queue, url, pool


class SankakuAPI():
    """Interface for the sankaku.app API"""
    ROOT = "https://sankakuapi.com"
    VERSION = None

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Accept"     : "application/vnd.sankaku.api+json;v=2",
            "Api-Version": self.VERSION,
            "Origin"     : extractor.root,
        }

        self.username, self.password = extractor._get_auth_info()
        if not self.username:
            self.authenticate = util.noop

    def notes(self, post_id):
        params = {"lang": "en"}
        return self._call(f"/posts/{post_id}/notes", params)

    def tags(self, post_id):
        endpoint = f"/posts/{post_id}/tags"
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
        url = self.ROOT + endpoint
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
                try:
                    code = f"'{code.rpartition('__')[2].replace('-', ' ')}'"
                except Exception:
                    pass
                raise exception.AbortExtraction(code)
            return data

    def _pagination(self, endpoint, params):
        params["lang"] = "en"
        params["limit"] = str(self.extractor.per_page)

        if refresh := self.extractor.config("refresh", False):
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
                        if url := post["file_url"]:
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

    api = extr.api
    url = api.ROOT + "/auth/token"
    data = {"login": username, "password": password}

    response = extr.request(
        url, method="POST", headers=api.headers, json=data, fatal=False)
    data = response.json()

    if response.status_code >= 400 or not data.get("success"):
        raise exception.AuthenticationError(data.get("error"))
    return "Bearer " + data["access_token"]
