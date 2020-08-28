# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://gelbooru.com/"""

from . import booru
from .common import Message
from .. import text


class GelbooruExtractor(booru.XmlParserMixin,
                        booru.GelbooruPageMixin,
                        booru.BooruExtractor):
    """Base class for gelbooru extractors"""
    category = "gelbooru"
    api_url = "https://gelbooru.com/index.php"
    post_url = "https://gelbooru.com/index.php?page=post&s=view&id={}"
    pool_url = "https://gelbooru.com/index.php?page=pool&s=show&id={}"

    def __init__(self, match):
        super().__init__(match)

        self.use_api = self.config("api", True)
        if self.use_api:
            self.params.update({"page": "dapi", "s": "post", "q": "index"})
        else:
            self.items = self.items_noapi
            self.session.cookies["fringeBenefits"] = "yup"
            self.per_page = 42

    def items_noapi(self):
        yield Message.Version, 1
        data = self.get_metadata()

        for post in self.get_posts():
            post = self.get_post_data(post)
            url = post["file_url"]
            post.update(data)
            text.nameext_from_url(url, post)
            yield Message.Directory, post
            yield Message.Url, url, post

    def get_posts(self):
        """Return an iterable containing all relevant post objects"""
        url = "https://gelbooru.com/index.php?page=post&s=list"
        params = {
            "tags": self.params["tags"],
            "pid" : self.page_start * self.per_page
        }

        while True:
            page = self.request(url, params=params).text
            ids = list(text.extract_iter(page, '<span id="s', '"'))
            yield from ids
            if len(ids) < self.per_page:
                return
            params["pid"] += self.per_page

    def get_post_data(self, post_id):
        """Extract metadata of a single post"""
        page = self.request(self.post_url.format(post_id)).text
        data = text.extract_all(page, (
            (None        , '<meta name="keywords"', ''),
            ("tags"      , ' imageboard- ', '"'),
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
        if self.extags:
            self.extended_tags(data, page)
        return data


class GelbooruTagExtractor(booru.TagMixin, GelbooruExtractor):
    """Extractor for images from gelbooru.com based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=list&tags=(?P<tags>[^&#]+)")
    test = (
        ("https://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
            "count": 5,
        }),
        ("https://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
            "options": (("api", False),),
            "count": 5,
        }),
    )


class GelbooruPoolExtractor(booru.PoolMixin, GelbooruExtractor):
    """Extractor for image-pools from gelbooru.com"""
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=pool&s=show&id=(?P<pool>\d+)")
    test = (
        ("https://gelbooru.com/index.php?page=pool&s=show&id=761", {
            "count": 6,
        }),
        ("https://gelbooru.com/index.php?page=pool&s=show&id=761", {
            "options": (("api", False),),
            "count": 6,
        }),
    )


class GelbooruPostExtractor(booru.PostMixin, GelbooruExtractor):
    """Extractor for single images from gelbooru.com"""
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=view&id=(?P<post>\d+)")
    test = ("https://gelbooru.com/index.php?page=post&s=view&id=313638", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
        "count": 1,
    })

    def get_posts(self):
        return (self.post,)
