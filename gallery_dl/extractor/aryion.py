# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://aryion.com/"""

from .common import Extractor, Message
from .. import text, util


BASE_PATTERN = r"(?:https?://)?(?:www\.)?aryion\.com/g4"


class AryionExtractor(Extractor):
    """Base class for aryion extractors"""
    category = "aryion"
    directory_fmt = ("{category}", "{user!l}", "{path:J - }")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    root = "https://aryion.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.offset = 0

    def items(self):
        for post_id in util.advance(self.posts(), self.offset):
            post = self._parse_post(post_id)
            if post:
                yield Message.Directory, post
                yield Message.Url, post["url"], post

    def posts(self):
        return ()

    def skip(self, num):
        self.offset += num
        return num

    def _parse_post(self, post_id):
        url = "{}/g4/view/{}".format(self.root, post_id)
        extr = text.extract_from(self.request(url).text)

        url = extr('property="og:image:secure_url" content="', '"')
        if not url:
            return None

        title, _, artist = text.unescape(extr(
            'property="og:title" content="', '"')).rpartition(" by ")
        data = text.nameext_from_url(url, {
            "id"    : text.parse_int(post_id),
            "url"   : url,
            "user"  : self.user or artist,
            "title" : title,
            "artist": artist,
            "path"  : text.split_html(extr("cookiecrumb'>", '</span'))[4:-1:2],
            "date"  : extr("class='pretty-date' title='", "'"),
            "views" : text.parse_int(extr("Views</b>:", "<").replace(",", "")),
            "size"  : text.parse_bytes(extr("File size</b>:", "<")[:-2]),
            "width" : text.parse_int(extr("Resolution</b>:", "x")),
            "height": text.parse_int(extr("", "<")),
            "comments" : text.parse_int(extr("Comments</b>:", "<")),
            "favorites": text.parse_int(extr("Favorites</b>:", "<")),
            "tags"  : text.split_html(extr("class='taglist'>", "</span>")),
            "description": text.remove_html(extr("<p>", "</p>"), "", ""),
        })

        d1, _, d2 = data["date"].partition(",")
        data["date"] = text.parse_datetime(d1[:-2] + d2, "%b %d %Y %I:%M %p")

        return data


class AryionGalleryExtractor(AryionExtractor):
    """Extractor for a user's gallery on eka's portal"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/(?:gallery/|user/|latest.php\?name=)([^/?&#]+)"
    test = (
        ("https://aryion.com/g4/gallery/jameshoward", {
            "pattern": r"https://aryion.com/g4/data/[^/]+/jameshoward-\d+-\w+",
            "range": "48-52",
            "count": 5,
        }),
        ("https://aryion.com/g4/user/jameshoward"),
        ("https://aryion.com/g4/latest.php?name=jameshoward"),
    )

    def posts(self):
        url = "{}/g4/latest.php?name={}".format(self.root, self.user)

        while True:
            page = self.request(url).text
            yield from text.extract_iter(
                page, "class='thumb' href='/g4/view/", "'")

            pos = page.find("Next &gt;&gt;")
            if pos < 0:
                return
            url = self.root + text.rextract(page, "href='", "'", pos)[0]


class AryionPostExtractor(AryionExtractor):
    """Extractor for individual posts on eka's portal"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/view/(\d+)"
    test = ("https://aryion.com/g4/view/510079", {
        "url": "b551444173ec73d369d5dd3e5d74054b4a45baa5",
        "keyword": {
            "artist"   : "jameshoward",
            "user"     : "jameshoward",
            "filename" : "jameshoward-510079-subscribestar_150",
            "extension": "jpg",
            "id"       : 510079,
            "width"    : 1665,
            "height"   : 1619,
            "size"     : 784241,
            "title"    : "I'm on subscribestar now too!",
            "description": r"re:Doesn't hurt to have a backup, right\?",
            "tags"     : ["Non-Vore", "subscribestar"],
            "date"     : "dt:2019-02-16 14:30:00",
            "path"     : [],
            "views"    : int,
            "favorites": int,
            "comments" : int,
        },
    })

    def posts(self):
        post_id = self.user
        self.user = None
        return (post_id,)
