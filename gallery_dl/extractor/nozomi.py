# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nozomi.la/"""

from .common import Extractor, Message
from .. import text


def decode_nozomi(n):
    for i in range(0, len(n), 4):
        yield (n[i] << 24) + (n[i+1] << 16) + (n[i+2] << 8) + n[i+3]


class NozomiExtractor(Extractor):
    """Base class for nozomi extractors"""
    category = "nozomi"
    root = "https://nozomi.la"
    filename_fmt = "{postid} {dataid}.{extension}"
    archive_fmt = "{dataid}"

    def items(self):

        data = self.metadata()
        self.session.headers["Origin"] = self.root
        self.session.headers["Referer"] = self.root + "/"

        for post_id in map(str, self.posts()):
            url = "https://j.nozomi.la/post/{}/{}/{}.json".format(
                post_id[-1], post_id[-3:-1], post_id)
            response = self.request(url, fatal=False)

            if response.status_code >= 400:
                self.log.warning(
                    "Skipping post %s ('%s %s')",
                    post_id, response.status_code, response.reason)
                continue

            post = response.json()
            post["tags"] = self._list(post.get("general"))
            post["artist"] = self._list(post.get("artist"))
            post["copyright"] = self._list(post.get("copyright"))
            post["character"] = self._list(post.get("character"))

            try:
                post["date"] = text.parse_datetime(
                    post["date"] + ":00", "%Y-%m-%d %H:%M:%S%z")
            except Exception:
                post["date"] = None

            post.update(data)

            images = post["imageurls"]
            for key in ("general", "imageurl", "imageurls"):
                if key in post:
                    del post[key]

            yield Message.Directory, post
            for post["num"], image in enumerate(images, 1):
                post["filename"] = post["dataid"] = did = image["dataid"]
                post["extension"] = ext = image["type"]
                post["is_video"] = video = bool(image.get("is_video"))
                post["url"] = url = "https://{}.nozomi.la/{}/{}/{}.{}".format(
                    "v" if video else "i", did[-1], did[-3:-1], did, ext)
                yield Message.Url, url, post

    def posts(self):
        url = "https://n.nozomi.la" + self.nozomi
        offset = (text.parse_int(self.pnum, 1) - 1) * 256

        while True:
            headers = {"Range": "bytes={}-{}".format(offset, offset+255)}
            response = self.request(url, headers=headers)
            yield from decode_nozomi(response.content)

            offset += 256
            cr = response.headers.get("Content-Range", "").rpartition("/")[2]
            if text.parse_int(cr, offset) <= offset:
                return

    def metadata(self):
        return {}

    @staticmethod
    def _list(src):
        return [x["tagname_display"] for x in src] if src else ()


class NozomiPostExtractor(NozomiExtractor):
    """Extractor for individual posts on nozomi.la"""
    subcategory = "post"
    pattern = r"(?:https?://)?nozomi\.la/post/(\d+)"
    test = (
        ("https://nozomi.la/post/3649262.html", {
            "url": "f4522adfc8159355fd0476de28761b5be0f02068",
            "content": "cd20d2c5149871a0b80a1b0ce356526278964999",
            "keyword": {
                "artist"   : ["hammer (sunset beach)"],
                "character": ["patchouli knowledge"],
                "copyright": ["touhou"],
                "dataid"   : "re:aaa9f7c632cde1e1a5baaff3fb6a6d857ec73df7fdc5",
                "date"     : "dt:2016-07-26 02:32:03",
                "extension": "jpg",
                "filename" : str,
                "height"   : 768,
                "is_video" : False,
                "postid"   : 3649262,
                "tags"     : list,
                "type"     : "jpg",
                "url"      : str,
                "width"    : 1024,
            },
        }),
        #  multiple images per post
        ("https://nozomi.la/post/25588032.html", {
            "url": "6aa3b7db385abcc9d374bdffd19187bccbf8f228",
            "keyword": "2a2998af93c6438863c4077bd386b613b8bc2957",
            "count": 7,
        }),
        # empty 'date' (#1163)
        ("https://nozomi.la/post/130309.html", {
            "keyword": {"date": None},
        })
    )

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self.post_id,)


class NozomiIndexExtractor(NozomiExtractor):
    """Extractor for the nozomi.la index"""
    subcategory = "index"
    pattern = (r"(?:https?://)?nozomi\.la/"
               r"(?:(index(?:-Popular)?)-(\d+)\.html)?(?:$|#|\?)")
    test = (
        ("https://nozomi.la/"),
        ("https://nozomi.la/index-2.html"),
        ("https://nozomi.la/index-Popular-33.html"),
    )

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        index, self.pnum = match.groups()
        self.nozomi = "/{}.nozomi".format(index or "index")


class NozomiTagExtractor(NozomiExtractor):
    """Extractor for posts from tag searches on nozomi.la"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{dataid}"
    pattern = r"(?:https?://)?nozomi\.la/tag/([^/?#]+)-(\d+)\."
    test = ("https://nozomi.la/tag/3:1_aspect_ratio-1.html", {
        "pattern": r"^https://[iv]\.nozomi\.la/\w/\w\w/\w+\.\w+$",
        "count": ">= 25",
        "range": "1-25",
    })

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        tags, self.pnum = match.groups()
        self.tags = text.unquote(tags)
        self.nozomi = "/nozomi/{}.nozomi".format(self.tags)

    def metadata(self):
        return {"search_tags": self.tags}


class NozomiSearchExtractor(NozomiExtractor):
    """Extractor for search results on nozomi.la"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags:J }")
    archive_fmt = "t_{search_tags}_{dataid}"
    pattern = r"(?:https?://)?nozomi\.la/search\.html\?q=([^&#]+)"
    test = ("https://nozomi.la/search.html?q=hibiscus%203:4_ratio#1", {
        "count": ">= 5",
    })

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1)).split()

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        result = None
        positive = []
        negative = []

        def nozomi(path):
            url = "https://j.nozomi.la/" + path + ".nozomi"
            return decode_nozomi(self.request(url).content)

        for tag in self.tags:
            (negative if tag[0] == "-" else positive).append(
                tag.replace("/", ""))

        for tag in positive:
            ids = nozomi("nozomi/" + tag)
            if result is None:
                result = set(ids)
            else:
                result.intersection_update(ids)

        if result is None:
            result = set(nozomi("index"))
        for tag in negative:
            result.difference_update(nozomi("nozomi/" + tag[1:]))

        return sorted(result, reverse=True) if result else ()
