# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danbooru.donmai.us/ and other Danbooru instances"""

from .common import BaseExtractor, Message
from .. import text, util
import datetime


class DanbooruExtractor(BaseExtractor):
    """Base class for danbooru extractors"""
    basecategory = "Danbooru"
    filename_fmt = "{category}_{id}_{filename}.{extension}"
    page_limit = 1000
    page_start = None
    per_page = 200
    request_interval = (0.5, 1.5)

    def _init(self):
        self.ugoira = self.config("ugoira", False)
        self.external = self.config("external", False)
        self.includes = False

        threshold = self.config("threshold")
        if isinstance(threshold, int):
            self.threshold = 1 if threshold < 1 else threshold
        else:
            self.threshold = self.per_page

        username, api_key = self._get_auth_info()
        if username:
            self.log.debug("Using HTTP Basic Auth for user '%s'", username)
            self.session.auth = util.HTTPBasicAuth(username, api_key)

    def skip(self, num):
        pages = num // self.per_page
        if pages >= self.page_limit:
            pages = self.page_limit - 1
        self.page_start = pages + 1
        return pages * self.per_page

    def items(self):
        self.session.headers["User-Agent"] = util.USERAGENT

        includes = self.config("metadata")
        if includes:
            if isinstance(includes, (list, tuple)):
                includes = ",".join(includes)
            elif not isinstance(includes, str):
                includes = "artist_commentary,children,notes,parent,uploader"
            self.includes = includes + ",id"

        data = self.metadata()
        for post in self.posts():

            try:
                url = post["file_url"]
            except KeyError:
                if self.external and post["source"]:
                    post.update(data)
                    yield Message.Directory, post
                    yield Message.Queue, post["source"], post
                continue

            text.nameext_from_url(url, post)
            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            post["tags"] = (
                post["tag_string"].split(" ")
                if post["tag_string"] else ())
            post["tags_artist"] = (
                post["tag_string_artist"].split(" ")
                if post["tag_string_artist"] else ())
            post["tags_character"] = (
                post["tag_string_character"].split(" ")
                if post["tag_string_character"] else ())
            post["tags_copyright"] = (
                post["tag_string_copyright"].split(" ")
                if post["tag_string_copyright"] else ())
            post["tags_general"] = (
                post["tag_string_general"].split(" ")
                if post["tag_string_general"] else ())
            post["tags_meta"] = (
                post["tag_string_meta"].split(" ")
                if post["tag_string_meta"] else ())

            if post["extension"] == "zip":
                if self.ugoira:
                    post["_ugoira_original"] = False
                    post["_ugoira_frame_data"] = post["frames"] = \
                        self._ugoira_frames(post)
                    post["_http_adjust_extension"] = False
                else:
                    url = post["large_file_url"]
                    post["extension"] = "webm"

            if url[0] == "/":
                url = self.root + url

            post.update(data)
            yield Message.Directory, post
            yield Message.Url, url, post

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def _pagination(self, endpoint, params, prefix=None):
        url = self.root + endpoint
        params["limit"] = self.per_page
        params["page"] = self.page_start

        first = True
        while True:
            posts = self.request(url, params=params).json()
            if isinstance(posts, dict):
                posts = posts["posts"]

            if posts:
                if self.includes:
                    params_meta = {
                        "only" : self.includes,
                        "limit": len(posts),
                        "tags" : "id:" + ",".join(str(p["id"]) for p in posts),
                    }
                    data = {
                        meta["id"]: meta
                        for meta in self.request(
                            url, params=params_meta).json()
                    }
                    for post in posts:
                        post.update(data[post["id"]])

                if prefix == "a" and not first:
                    posts.reverse()

                yield from posts

            if len(posts) < self.threshold:
                return

            if prefix:
                params["page"] = "{}{}".format(prefix, posts[-1]["id"])
            elif params["page"]:
                params["page"] += 1
            else:
                params["page"] = 2
            first = False

    def _ugoira_frames(self, post):
        data = self.request("{}/posts/{}.json?only=media_metadata".format(
            self.root, post["id"])
        ).json()["media_metadata"]["metadata"]

        ext = data["ZIP:ZipFileName"].rpartition(".")[2]
        fmt = ("{:>06}." + ext).format
        delays = data["Ugoira:FrameDelays"]
        return [{"file": fmt(index), "delay": delay}
                for index, delay in enumerate(delays)]


BASE_PATTERN = DanbooruExtractor.update({
    "danbooru": {
        "root": None,
        "pattern": r"(?:(?:danbooru|hijiribe|sonohara|safebooru)\.donmai\.us"
                   r"|donmai\.moe)",
    },
    "atfbooru": {
        "root": "https://booru.allthefallen.moe",
        "pattern": r"booru\.allthefallen\.moe",
    },
    "aibooru": {
        "root": None,
        "pattern": r"(?:safe\.)?aibooru\.online",
    },
    "booruvar": {
        "root": "https://booru.borvar.art",
        "pattern": r"booru\.borvar\.art",
    },
})


class DanbooruTagExtractor(DanbooruExtractor):
    """Extractor for danbooru posts from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/posts\?(?:[^&#]*&)*tags=([^&#]*)"
    example = "https://danbooru.donmai.us/posts?tags=TAG"

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        prefix = "b"
        for tag in self.tags.split():
            if tag.startswith("order:"):
                if tag == "order:id" or tag == "order:id_asc":
                    prefix = "a"
                elif tag == "order:id_desc":
                    prefix = "b"
                else:
                    prefix = None
            elif tag.startswith(
                    ("id:", "md5", "ordfav:", "ordfavgroup:", "ordpool:")):
                prefix = None
                break

        return self._pagination("/posts.json", {"tags": self.tags}, prefix)


class DanbooruPoolExtractor(DanbooruExtractor):
    """Extractor for posts from danbooru pools"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name]}")
    archive_fmt = "p_{pool[id]}_{id}"
    pattern = BASE_PATTERN + r"/pool(?:s|/show)/(\d+)"
    example = "https://danbooru.donmai.us/pools/12345"

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)

    def metadata(self):
        url = "{}/pools/{}.json".format(self.root, self.pool_id)
        pool = self.request(url).json()
        pool["name"] = pool["name"].replace("_", " ")
        self.post_ids = pool.pop("post_ids", ())
        return {"pool": pool}

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination("/posts.json", params, "b")


class DanbooruPostExtractor(DanbooruExtractor):
    """Extractor for single danbooru posts"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post(?:s|/show)/(\d+)"
    example = "https://danbooru.donmai.us/posts/12345"

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        url = "{}/posts/{}.json".format(self.root, self.post_id)
        post = self.request(url).json()
        if self.includes:
            params = {"only": self.includes}
            post.update(self.request(url, params=params).json())
        return (post,)


class DanbooruPopularExtractor(DanbooruExtractor):
    """Extractor for popular images from danbooru"""
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = BASE_PATTERN + r"/(?:explore/posts/)?popular(?:\?([^#]*))?"
    example = "https://danbooru.donmai.us/explore/posts/popular"

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.params = match.group(match.lastindex)

    def metadata(self):
        self.params = params = text.parse_query(self.params)
        scale = params.get("scale", "day")
        date = params.get("date") or datetime.date.today().isoformat()

        if scale == "week":
            date = datetime.date.fromisoformat(date)
            date = (date - datetime.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        return self._pagination("/explore/posts/popular.json", self.params)
