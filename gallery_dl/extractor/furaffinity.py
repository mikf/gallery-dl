# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.furaffinity.net/"""

from .common import Extractor, Message
from .. import text, util


BASE_PATTERN = r"(?:https?://)?(?:www\.)?furaffinity\.net"


class FuraffinityExtractor(Extractor):
    """Base class for furaffinity extractors"""
    category = "furaffinity"
    directory_fmt = ("{category}", "{user!l}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.furaffinity.net"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.offset = 0

    def items(self):
        for post_id in util.advance(self.posts(), self.offset):
            post = self._parse_post(post_id)
            if post:
                yield Message.Directory, post
                text.nameext_from_url(post["url"], post)
                yield Message.Url, post["url"], post

    def posts(self):
        return self._pagination()

    def skip(self, num):
        self.offset += num
        return num

    def _parse_post(self, post_id):
        url = "{}/view/{}/".format(self.root, post_id)
        extr = text.extract_from(self.request(url).text)

        title, _, artist = text.unescape(extr(
            'property="og:title" content="', '"')).rpartition(" by ")
        if not extr('class="download', '>'):
            self.log.warning(
                "Unable to download post %s (\"%s\")", post_id,
                text.remove_html(extr('class="link-override">', '</p>')))
            return None

        return {
            "id"    : text.parse_int(post_id),
            "title" : title,
            "artist": artist,
            "user"  : self.user or artist,
            "url"   : "https:" + extr('href="', '"'),
            "tags"  : text.split_html(extr('class="tags-row">', '</section>')),
            "date"  : text.parse_datetime(extr(
                '<strong><span title="', '"'), "%b %d, %Y %I:%M %p"),
            "description": text.unescape(text.remove_html(extr(
                '<div class="submission-description">', '</div>'), "", "")),
        }

    def _pagination(self):
        num = 1

        while True:
            url = "{}/{}/{}/{}/".format(
                self.root, self.subcategory, self.user, num)
            page = self.request(url).text
            post_id = None

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not post_id:
                return
            num += 1

    def _pagination_favorites(self):
        path = "/favorites/{}/".format(self.user)

        while path:
            page = self.request(self.root + path).text
            yield from text.extract_iter(page, 'id="sid-', '"')
            path = text.extract(page, 'button standard right" href="', '"')[0]


class FuraffinityGalleryExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's gallery"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/gallery/([^/?&#]+)"
    test = ("https://www.furaffinity.net/gallery/mirlinthloth/", {
        "pattern": r"https://d.facdn.net/art/mirlinthloth/\d+/\d+.\w+\.\w+",
        "range": "45-50",
        "count": 6,
    })


class FuraffinityScrapsExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user!l}", "Scraps")
    pattern = BASE_PATTERN + r"/scraps/([^/?&#]+)"
    test = ("https://www.furaffinity.net/scraps/mirlinthloth/", {
        "pattern": r"https://d.facdn.net/art/[^/]+(/stories)?/\d+/\d+.\w+.\w+",
        "count": ">= 3",
    })


class FuraffinityFavoriteExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user!l}", "Favorites")
    pattern = BASE_PATTERN + r"/favorites/([^/?&#]+)"
    test = ("https://www.furaffinity.net/favorites/mirlinthloth/", {
        "pattern": r"https://d.facdn.net/art/[^/]+/\d+/\d+.\w+\.\w+",
        "range": "45-50",
        "count": 6,
    })

    def posts(self):
        return self._pagination_favorites()


class FuraffinityPostExtractor(FuraffinityExtractor):
    """Extractor for individual posts on furaffinity"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/view/(\d+)"
    test = ("https://www.furaffinity.net/view/21835115/", {
        "url": "eae4ef93d99365c69b31a37561bd800c03d336ad",
        "keyword": {
            "artist"     : "mirlinthloth",
            "date"       : "type:datetime",
            "description": "A Song made playing the game Cosmic DJ.",
            "extension"  : "mp3",
            "filename"   : r"re:\d+\.mirlinthloth_dj_fennmink_-_bude_s_4_ever",
            "id"         : 21835115,
            "tags"       : list,
            "title"      : "Bude's 4 Ever",
            "url"        : "re:https://d.facdn.net/art/mirlinthloth/music/",
            "user"       : "mirlinthloth",
        },
    })

    def posts(self):
        post_id = self.user
        self.user = None
        return (post_id,)


class FuraffinityUserExtractor(FuraffinityExtractor):
    """Extractor for furaffinity user profiles"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?&#]+)"
    test = (
        ("https://www.furaffinity.net/user/mirlinthloth/", {
            "pattern": r"/gallery/mirlinthloth/$",
        }),
        ("https://www.furaffinity.net/user/mirlinthloth/", {
            "options": (("include", "all"),),
            "pattern": r"/(gallery|scraps|favorites)/mirlinthloth/$",
            "count": 3,
        }),
    )

    def items(self):
        base = "{}/{{}}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (FuraffinityGalleryExtractor , base.format("gallery")),
            (FuraffinityScrapsExtractor  , base.format("scraps")),
            (FuraffinityFavoriteExtractor, base.format("favorites")),
        ), ("gallery",))
