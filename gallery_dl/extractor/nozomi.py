# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
    domain = "gold-usergeneratedcontent.net"
    filename_fmt = "{postid} {dataid}.{extension}"
    archive_fmt = "{dataid}"

    def _init(self):
        self.session.headers["Origin"] = self.root

    def items(self):
        data = self.metadata()

        for post_id in map(str, self.posts()):
            url = "https://j.{}/post/{}/{}/{}.json".format(
                self.domain, post_id[-1], post_id[-3:-1], post_id)
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
                post["is_video"] = video = \
                    True if image.get("is_video") else False

                ext = image["type"]
                if video:
                    subdomain = "v"
                elif ext == "gif":
                    subdomain = "g"
                else:
                    subdomain = "w"
                    ext = "webp"

                post["extension"] = ext
                post["url"] = url = "https://{}.{}/{}/{}/{}.{}".format(
                    subdomain, self.domain, did[-1], did[-3:-1], did, ext)
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
    example = "https://nozomi.la/post/12345.html"

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
    example = "https://nozomi.la/index-1.html"

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
    example = "https://nozomi.la/tag/TAG-1.html"

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
    example = "https://nozomi.la/search.html?q=QUERY"

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
            url = "https://j.{}/{}.nozomi".format(self.domain, path)
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
