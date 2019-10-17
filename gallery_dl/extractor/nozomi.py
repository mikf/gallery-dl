# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nozomi.la/"""

from .common import Extractor, Message
from .. import text


class NozomiExtractor(Extractor):
    """Base class for nozomi extractors"""
    category = "nozomi"
    root = "https://nozomi.la"
    filename_fmt = "{postid}.{extension}"
    archive_fmt = "{postid}"

    def items(self):
        yield Message.Version, 1

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

            image = response.json()
            image["tags"] = self._list(image.get("general"))
            image["artist"] = self._list(image.get("artist"))
            image["copyright"] = self._list(image.get("copyright"))
            image["character"] = self._list(image.get("character"))
            image["is_video"] = bool(image.get("is_video"))
            image["date"] = text.parse_datetime(
                image["date"] + ":00", "%Y-%m-%d %H:%M:%S%z")
            image["url"] = text.urljoin(self.root, image["imageurl"])
            text.nameext_from_url(image["url"], image)
            image.update(data)

            for key in ("general", "imageurl", "imageurls"):
                if key in image:
                    del image[key]

            yield Message.Directory, image
            yield Message.Url, image["url"], image

    def metadata(self):
        return {}

    def posts(self):
        return ()

    @staticmethod
    def _list(src):
        if not src:
            return []
        return [x["tagname_display"] for x in src]

    @staticmethod
    def _unpack(b):
        for i in range(0, len(b), 4):
            yield (b[i] << 24) + (b[i+1] << 16) + (b[i+2] << 8) + b[i+3]


class NozomiPostExtractor(NozomiExtractor):
    """Extractor for individual posts on nozomi.la"""
    subcategory = "post"
    pattern = r"(?:https?://)?nozomi\.la/post/(\d+)"
    test = ("https://nozomi.la/post/3649262.html", {
        "url": "f4522adfc8159355fd0476de28761b5be0f02068",
        "content": "cd20d2c5149871a0b80a1b0ce356526278964999",
        "keyword": {
            "artist"   : ["hammer (sunset beach)"],
            "character": ["patchouli knowledge"],
            "copyright": ["touhou"],
            "dataid"   : "re:aaa9f7c632cde1e1a5baaff3fb6a6d857ec73df7fdc5cf5a",
            "date"     : "type:datetime",
            "extension": "jpg",
            "favorites": int,
            "filename" : str,
            "height"   : 768,
            "is_video" : False,
            "postid"   : 3649262,
            "source"   : "danbooru",
            "sourceid" : 2434215,
            "tags"     : list,
            "type"     : "jpg",
            "url"      : str,
            "width"    : 1024,
        },
    })

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self.post_id,)


class NozomiTagExtractor(NozomiExtractor):
    """Extractor for posts from tag searches on nozomi.la"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{postid}"
    pattern = r"(?:https?://)?nozomi\.la/tag/([^/?&#]+)-\d+\."
    test = ("https://nozomi.la/tag/3:1_aspect_ratio-1.html", {
        "pattern": r"^https://i.nozomi.la/\w/\w\w/\w+\.\w+$",
        "count": ">= 75",
        "range": "1-75",
    })

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1)).lower()

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        url = "https://n.nozomi.la/nozomi/{}.nozomi".format(self.tags)
        i = 0

        while True:
            headers = {"Range": "bytes={}-{}".format(i, i+255)}
            response = self.request(url, headers=headers)
            yield from self._unpack(response.content)

            i += 256
            cr = response.headers.get("Content-Range", "").rpartition("/")[2]
            if text.parse_int(cr, i) <= i:
                return


class NozomiSearchExtractor(NozomiExtractor):
    """Extractor for search results on nozomi.la"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags:J }")
    archive_fmt = "t_{search_tags}_{postid}"
    pattern = r"(?:https?://)?nozomi\.la/search\.html\?q=([^&#]+)"
    test = ("https://nozomi.la/search.html?q=hibiscus%203:4_ratio#1", {
        "count": ">= 5",
    })

    def __init__(self, match):
        NozomiExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1)).lower().split()

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        index = None
        result = set()

        def nozomi(path):
            url = "https://j.nozomi.la/" + path + ".nozomi"
            return self._unpack(self.request(url).content)

        for tag in self.tags:
            if tag[0] == "-":
                if not index:
                    index = set(nozomi("index"))
                items = index.difference(nozomi("nozomi/" + tag[1:]))
            else:
                items = nozomi("nozomi/" + tag)

            if result:
                result.intersection_update(items)
            else:
                result.update(items)

        return result
