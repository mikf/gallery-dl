# -*- coding: utf-8 -*-

# Copyright 2014-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danbooru.donmai.us/ and other Danbooru instances"""

from .common import BaseExtractor, Message
from .. import text, util, dt


class DanbooruExtractor(BaseExtractor):
    """Base class for danbooru extractors"""
    basecategory = "Danbooru"
    filename_fmt = "{category}_{id}_{filename}.{extension}"
    page_limit = 1000
    page_start = None
    per_page = 200
    useragent = util.USERAGENT
    request_interval = (0.5, 1.5)

    def _init(self):
        self.ugoira = self.config("ugoira", False)
        self.external = self.config("external", False)
        self.includes = False

        threshold = self.config("threshold")
        if isinstance(threshold, int):
            self.threshold = 1 if threshold < 1 else threshold
        else:
            self.threshold = self.per_page - 20

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
        # 'includes' initialization must be done here and not in '_init()'
        # or it'll cause an exception with e621 when 'metadata' is enabled
        if includes := self.config("metadata"):
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
                    yield Message.Directory, "", post
                    yield Message.Queue, post["source"], post
                continue

            text.nameext_from_url(url, post)
            post["date"] = dt.parse_iso(post["created_at"])

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
                if url[1] == "/":
                    url = "https:" + url
                else:
                    url = self.root + url

            post.update(data)
            yield Message.Directory, "", post
            yield Message.Url, url, post

    def items_artists(self):
        for artist in self.artists():
            artist["_extractor"] = DanbooruTagExtractor
            url = f"{self.root}/posts?tags={text.quote(artist['name'])}"
            yield Message.Queue, url, artist

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
            posts = self.request_json(url, params=params)
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
                        for meta in self.request_json(url, params=params_meta)
                    }
                    for post in posts:
                        post.update(data[post["id"]])

                if prefix == "a" and not first:
                    posts.reverse()

                yield from posts

            if len(posts) < self.threshold:
                return

            if prefix:
                params["page"] = f"{prefix}{posts[-1]['id']}"
            elif params["page"]:
                params["page"] += 1
            else:
                params["page"] = 2
            first = False

    def _ugoira_frames(self, post):
        data = self.request_json(
            f"{self.root}/posts/{post['id']}.json?only=media_metadata"
        )["media_metadata"]["metadata"]

        if "Ugoira:FrameMimeType" in data:
            ext = data["Ugoira:FrameMimeType"].rpartition("/")[2]
            if ext == "jpeg":
                ext = "jpg"
        else:
            ext = data["ZIP:ZipFileName"].rpartition(".")[2]

        fmt = ("{:>06}." + ext).format
        delays = data["Ugoira:FrameDelays"]
        return [{"file": fmt(index), "delay": delay}
                for index, delay in enumerate(delays)]

    def _collection_posts(self, cid, ctype):
        reverse = prefix = None

        order = self.config("order-posts")
        if not order or order in {"asc", "pool", "pool_asc", "asc_pool"}:
            params = {"tags": f"ord{ctype}:{cid}"}
        elif order in {"id", "desc_id", "id_desc"}:
            params = {"tags": f"{ctype}:{cid}"}
            prefix = "b"
        elif order in {"desc", "desc_pool", "pool_desc"}:
            params = {"tags": f"ord{ctype}:{cid}"}
            reverse = True
        elif order in {"asc_id", "id_asc"}:
            params = {"tags": f"{ctype}:{cid}"}
            reverse = True

        posts = self._pagination("/posts.json", params, prefix)
        if reverse:
            self.log.info("Collecting posts of %s %s", ctype, cid)
            return self._collection_enumerate_reverse(posts)
        else:
            return self._collection_enumerate(posts)

    def _collection_metadata(self, cid, ctype, cname=None):
        url = f"{self.root}/{cname or ctype}s/{cid}.json"
        collection = self.request_json(url)
        collection["name"] = collection["name"].replace("_", " ")
        self.post_ids = collection.pop("post_ids", ())
        return {ctype: collection}

    def _collection_enumerate(self, posts):
        pid_to_num = {pid: num for num, pid in enumerate(self.post_ids, 1)}
        for post in posts:
            post["num"] = pid_to_num[post["id"]]
            yield post

    def _collection_enumerate_reverse(self, posts):
        posts = list(posts)
        posts.reverse()

        pid_to_num = {pid: num for num, pid in enumerate(self.post_ids, 1)}
        for post in posts:
            post["num"] = pid_to_num[post["id"]]
        return posts


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
        "pattern": r"(?:safe\.|general\.)?aibooru\.(?:online|download)",
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
    pattern = rf"{BASE_PATTERN}/posts\?(?:[^&#]*&)*tags=([^&#]*)"
    example = "https://danbooru.donmai.us/posts?tags=TAG"

    def metadata(self):
        self.tags = text.unquote(self.groups[-1].replace("+", " "))
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
                    ("id:", "md5:", "ordfav:", "ordfavgroup:", "ordpool:")):
                prefix = None
                break

        return self._pagination("/posts.json", {"tags": self.tags}, prefix)


class DanbooruRandomExtractor(DanbooruTagExtractor):
    """Extractor for a random danbooru post"""
    subcategory = "random"
    pattern = rf"{BASE_PATTERN}/posts/random(?:\?(?:[^&#]*&)*tags=([^&#]*))?"
    example = "https://danbooru.donmai.us/posts/random?tags=TAG"

    def metadata(self):
        tags = self.groups[-1] or ""
        self.tags = text.unquote(tags.replace("+", " "))
        return {"search_tags": self.tags}

    def posts(self):
        posts = self.request_json(self.root + "/posts/random.json",
                                  params={"tags": self.tags or None})
        return (posts,) if isinstance(posts, dict) else posts


class DanbooruPoolExtractor(DanbooruExtractor):
    """Extractor for Danbooru pools"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name]}")
    filename_fmt = "{num:>04}_{id}_{filename}.{extension}"
    archive_fmt = "p_{pool[id]}_{id}"
    pattern = rf"{BASE_PATTERN}/pool(?:s|/show)/(\d+)"
    example = "https://danbooru.donmai.us/pools/12345"

    def metadata(self):
        self.pool_id = self.groups[-1]
        return self._collection_metadata(self.pool_id, "pool")

    def posts(self):
        return self._collection_posts(self.pool_id, "pool")


class DanbooruFavgroupExtractor(DanbooruExtractor):
    """Extractor for Danbooru favorite groups"""
    subcategory = "favgroup"
    directory_fmt = ("{category}", "Favorite Groups",
                     "{favgroup[id]} {favgroup[name]}")
    filename_fmt = "{num:>04}_{id}_{filename}.{extension}"
    archive_fmt = "fg_{favgroup[id]}_{id}"
    pattern = rf"{BASE_PATTERN}/favorite_group(?:s|/show)/(\d+)"
    example = "https://danbooru.donmai.us/favorite_groups/12345"

    def metadata(self):
        return self._collection_metadata(
            self.groups[-1], "favgroup", "favorite_group")

    def posts(self):
        return self._collection_posts(self.groups[-1], "favgroup")


class DanbooruPostExtractor(DanbooruExtractor):
    """Extractor for single danbooru posts"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = rf"{BASE_PATTERN}/post(?:s|/show)/(\d+)"
    example = "https://danbooru.donmai.us/posts/12345"

    def posts(self):
        url = f"{self.root}/posts/{self.groups[-1]}.json"
        post = self.request_json(url)
        if self.includes:
            params = {"only": self.includes}
            post.update(self.request_json(url, params=params))
        return (post,)


class DanbooruMediaassetExtractor(DanbooruExtractor):
    """Extractor for a danbooru media asset"""
    subcategory = "media-asset"
    filename_fmt = "{category}_ma{id}_{filename}.{extension}"
    archive_fmt = "m{id}"
    pattern = rf"{BASE_PATTERN}/media_assets/(\d+)"
    example = "https://danbooru.donmai.us/media_assets/12345"

    def posts(self):
        url = f"{self.root}/media_assets/{self.groups[-1]}.json"
        asset = self.request_json(url)

        asset["file_url"] = asset["variants"][-1]["url"]
        asset["tag_string"] = \
            asset["tag_string_artist"] = \
            asset["tag_string_character"] = \
            asset["tag_string_copyright"] = \
            asset["tag_string_general"] = \
            asset["tag_string_meta"] = ""

        if self.includes:
            params = {"only": self.includes}
            asset.update(self.request_json(url, params=params))
        return (asset,)


class DanbooruPopularExtractor(DanbooruExtractor):
    """Extractor for popular images from danbooru"""
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = rf"{BASE_PATTERN}/(?:explore/posts/)?popular(?:\?([^#]*))?"
    example = "https://danbooru.donmai.us/explore/posts/popular"

    def metadata(self):
        self.params = params = text.parse_query(self.groups[-1])
        scale = params.get("scale", "day")
        date = params.get("date") or dt.date.today().isoformat()

        if scale == "week":
            date = dt.date.fromisoformat(date)
            date = (date - dt.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        return self._pagination("/explore/posts/popular.json", self.params)


class DanbooruArtistExtractor(DanbooruExtractor):
    """Extractor for danbooru artists"""
    subcategory = "artist"
    pattern = rf"{BASE_PATTERN}/artists/(\d+)"
    example = "https://danbooru.donmai.us/artists/12345"

    items = DanbooruExtractor.items_artists

    def artists(self):
        url = f"{self.root}/artists/{self.groups[-1]}.json"
        return (self.request_json(url),)


class DanbooruArtistSearchExtractor(DanbooruExtractor):
    """Extractor for danbooru artist searches"""
    subcategory = "artist-search"
    pattern = rf"{BASE_PATTERN}/artists/?\?([^#]+)"
    example = "https://danbooru.donmai.us/artists?QUERY"

    items = DanbooruExtractor.items_artists

    def artists(self):
        url = self.root + "/artists.json"
        params = text.parse_query(self.groups[-1])
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            artists = self.request_json(url, params=params)

            yield from artists

            if len(artists) < 20:
                return
            params["page"] += 1
