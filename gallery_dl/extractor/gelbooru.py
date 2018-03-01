# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://gelbooru.com/"""

from .common import SharedConfigExtractor, Message
from .. import text, util, exception
import xml.etree.ElementTree as ET


class GelbooruExtractor(SharedConfigExtractor):
    """Base class for gelbooru extractors"""
    basecategory = "booru"
    category = "gelbooru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index"

    def __init__(self):
        SharedConfigExtractor.__init__(self)
        self.start_post = 0
        self.use_api = self.config("api", True)
        if self.use_api:
            self.get_post_data = self.get_post_data_api

    def items(self):
        data = self.get_metadata()

        yield Message.Version, 1
        yield Message.Directory, data

        for post in util.advance(self.get_posts(), self.start_post):
            if isinstance(post, str):
                post = self.get_post_data(post)
            for key in ("id", "width", "height", "score", "change"):
                post[key] = util.safe_int(post[key])
            url = post["file_url"]
            post.update(data)
            yield Message.Url, url, text.nameext_from_url(url, post)

    def skip(self, num):
        self.start_post += num
        return num

    def get_metadata(self):
        """Return general metadata"""
        return {}

    def get_posts(self):
        """Return an iterable containing all relevant post objects"""

    def get_post_data(self, post_id):
        """Extract metadata of a single post"""
        page = self.request("https://gelbooru.com/index.php?page=post&s=view"
                            "&id=" + post_id).text
        data = text.extract_all(page, (
            (None        , '<meta name="keywords"', ''),
            ("tags"      , ' imageboard, ', '"'),
            ("id"        , '<li>Id: ', '<'),
            ("created_at", '<li>Posted: ', '<'),
            ("width"     , '<li>Size: ', 'x'),
            ("height"    , '', '<'),
            ("source"    , '<li>Source: <a href="', '"'),
            ("rating"    , '<li>Rating: ', '<'),
            (None        , '<li>Score: ', ''),
            ("score"     , '>', '<'),
            ("file_url"  , '<li><a href="http', '"'),
            ("change"    , ' id="lupdated" value="', '"'),
        ))[0]
        data["file_url"] = "http" + data["file_url"].replace("m//", "m/", 1)
        data["md5"] = data["file_url"].rpartition("/")[2].partition(".")[0]
        data["rating"] = (data["rating"] or "?")[0].lower()
        data["tags"] = " ".join(
            [tag.replace(" ", "_") for tag in data["tags"].split(", ")])
        return data

    def get_post_data_api(self, post_id):
        """Request metadata of a single post from Gelbooru's API"""
        return ET.fromstring(
            self.request(self.api_url + "&id=" + post_id).text)[0].attrib


class GelbooruTagExtractor(GelbooruExtractor):
    """Extractor for images from gelbooru.com based on search-tags"""
    subcategory = "tag"
    directory_fmt = ["{category}", "{search_tags}"]
    archive_fmt = "t_{search_tags}_{id}"
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=list&tags=([^&]+)"]
    test = [
        ("https://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
            "count": 5,
        }),
        ("https://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
            "options": (("api", False),),
            "count": 5,
        }),
    ]

    def __init__(self, match):
        GelbooruExtractor.__init__(self)
        self.tags = text.unquote(match.group(1).replace("+", " "))
        self.per_page = 100 if self.use_api else 42
        self.start_page = 0

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        return num

    def get_metadata(self):
        return {"search_tags": self.tags}

    def get_posts(self):
        if self.use_api:
            return self._get_posts_api()
        return self._get_posts_manual()

    def _get_posts_api(self):
        params = {
            # 'pid' is page-id; first page has index 0
            "tags": self.tags, "limit": self.per_page, "pid": self.start_page}
        while True:
            root = ET.fromstring(
                self.request(self.api_url, params=params).text)
            for item in root:
                yield item.attrib
            if len(root) < self.per_page:
                return
            params["pid"] += 1

    def _get_posts_manual(self):
        url = "https://gelbooru.com/index.php?page=post&s=list"
        # 'pid' is post-id; values for 'pid' must be multiples of 42
        params = {"tags": self.tags, "pid": self.start_page * self.per_page}

        while True:
            page = self.request(url, params=params).text
            ids = list(text.extract_iter(page, '<a id="p', '"'))
            yield from ids
            if len(ids) < self.per_page:
                return
            params["pid"] += self.per_page


class GelbooruPoolExtractor(GelbooruExtractor):
    """Extractor for image-pools from gelbooru.com"""
    subcategory = "pool"
    directory_fmt = ["{category}", "pool", "{pool}"]
    archive_fmt = "p_{pool}_{id}"
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=pool&s=show&id=(\d+)"]
    test = [("https://gelbooru.com/index.php?page=pool&s=show&id=761", {
        "count": 6,
    })]

    def __init__(self, match):
        GelbooruExtractor.__init__(self)
        self.pool_id = match.group(1)
        self.posts = None

    def get_metadata(self):
        page = self.request("https://gelbooru.com/index.php?page=pool&s=show"
                            "&id=" + self.pool_id).text
        name, pos = text.extract(page, "<h3>Now Viewing: ", "</h3>")
        self.posts = list(text.extract_iter(page, 'id="p', '"', pos))

        if not name:
            raise exception.NotFoundError("pool")

        return {
            "pool": util.safe_int(self.pool_id),
            "pool_name": text.unescape(name),
            "count": len(self.posts),
        }

    def get_posts(self):
        return self.posts


class GelbooruPostExtractor(GelbooruExtractor):
    """Extractor for single images from gelbooru.com"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=view&id=(\d+)"]
    test = [("https://gelbooru.com/index.php?page=post&s=view&id=313638", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
        "count": 1,
    })]

    def __init__(self, match):
        GelbooruExtractor.__init__(self)
        self.post_id = match.group(1)

    def get_posts(self):
        return (self.post_id,)
