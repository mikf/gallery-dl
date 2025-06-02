# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hitomi.la/"""

from .common import GalleryExtractor, Extractor, Message
from .nozomi import decode_nozomi
from ..cache import memcache
from .. import text, util
import string
import re


class HitomiExtractor(Extractor):
    """Base class for hitomi extractors"""
    category = "hitomi"
    root = "https://hitomi.la"
    domain = "gold-usergeneratedcontent.net"


class HitomiGalleryExtractor(HitomiExtractor, GalleryExtractor):
    """Extractor for hitomi.la galleries"""
    pattern = (r"(?:https?://)?hitomi\.la"
               r"/(?:manga|doujinshi|cg|gamecg|imageset|galleries|reader)"
               r"/(?:[^/?#]+-)?(\d+)")
    example = "https://hitomi.la/manga/TITLE-867789.html"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match, False)
        self.gid = gid = self.groups[0]
        self.gallery_url = "https://ltn.{}/galleries/{}.js".format(
            self.domain, gid)

    def _init(self):
        self.session.headers["Referer"] = "{}/reader/{}.html".format(
            self.root, self.gid)

    def metadata(self, page):
        self.info = info = util.json_loads(page.partition("=")[2])
        iget = info.get

        language = iget("language")
        if language:
            language = language.capitalize()

        date = iget("date")
        if date:
            date += ":00"

        tags = []
        for tinfo in iget("tags") or ():
            tag = string.capwords(tinfo["tag"])
            if tinfo.get("female"):
                tag += " ♀"
            elif tinfo.get("male"):
                tag += " ♂"
            tags.append(tag)

        return {
            "gallery_id": text.parse_int(info["id"]),
            "title"     : info["title"],
            "title_jpn" : info.get("japanese_title") or "",
            "type"      : info["type"].capitalize(),
            "language"  : language,
            "lang"      : util.language_to_code(language),
            "date"      : text.parse_datetime(date, "%Y-%m-%d %H:%M:%S%z"),
            "tags"      : tags,
            "artist"    : [o["artist"] for o in iget("artists") or ()],
            "group"     : [o["group"] for o in iget("groups") or ()],
            "parody"    : [o["parody"] for o in iget("parodys") or ()],
            "characters": [o["character"] for o in iget("characters") or ()]
        }

    def images(self, _):
        # https://ltn.gold-usergeneratedcontent.net/gg.js
        gg_m, gg_b, gg_default = _parse_gg(self)

        fmt = ext = self.config("format") or "webp"
        check = (fmt != "webp")

        result = []
        for image in self.info["files"]:
            if check:
                ext = fmt if image.get("has" + fmt) else "webp"
            ihash = image["hash"]
            idata = text.nameext_from_url(image["name"])
            idata["extension_original"] = idata["extension"]
            idata["extension"] = ext

            # https://ltn.gold-usergeneratedcontent.net/common.js
            inum = int(ihash[-1] + ihash[-3:-1], 16)
            url = "https://{}{}.{}/{}/{}/{}.{}".format(
                ext[0], gg_m.get(inum, gg_default) + 1, self.domain,
                gg_b, inum, ihash, ext,
            )
            result.append((url, idata))
        return result


class HitomiTagExtractor(HitomiExtractor):
    """Extractor for galleries from tag searches on hitomi.la"""
    subcategory = "tag"
    pattern = (r"(?:https?://)?hitomi\.la"
               r"/(tag|artist|group|series|type|character)"
               r"/([^/?#]+)\.html")
    example = "https://hitomi.la/tag/TAG-LANG.html"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.type, self.tag = match.groups()

        tag, _, num = self.tag.rpartition("-")
        if num.isdecimal():
            self.tag = tag

    def items(self):
        data = {
            "_extractor": HitomiGalleryExtractor,
            "search_tags": text.unquote(self.tag.rpartition("-")[0]),
        }
        nozomi_url = "https://ltn.{}/{}/{}.nozomi".format(
            self.domain, self.type, self.tag)
        headers = {
            "Origin": self.root,
            "Cache-Control": "max-age=0",
        }

        offset = 0
        total = None
        while True:
            headers["Referer"] = "{}/{}/{}.html?page={}".format(
                self.root, self.type, self.tag, offset // 100 + 1)
            headers["Range"] = "bytes={}-{}".format(offset, offset+99)
            response = self.request(nozomi_url, headers=headers)

            for gallery_id in decode_nozomi(response.content):
                gallery_url = "{}/galleries/{}.html".format(
                    self.root, gallery_id)
                yield Message.Queue, gallery_url, data

            offset += 100
            if total is None:
                total = text.parse_int(
                    response.headers["content-range"].rpartition("/")[2])
            if offset >= total:
                return


class HitomiIndexExtractor(HitomiTagExtractor):
    """Extractor for galleries from index searches on hitomi.la"""
    subcategory = "index"
    pattern = r"(?:https?://)?hitomi\.la/(\w+)-(\w+)\.html"
    example = "https://hitomi.la/index-LANG.html"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.tag, self.language = match.groups()

    def items(self):
        data = {"_extractor": HitomiGalleryExtractor}
        nozomi_url = "https://ltn.{}/{}-{}.nozomi".format(
            self.domain, self.tag, self.language)
        headers = {
            "Origin": self.root,
            "Cache-Control": "max-age=0",
        }

        offset = 0
        total = None
        while True:
            headers["Referer"] = "{}/{}-{}.html?page={}".format(
                self.root, self.tag, self.language, offset // 100 + 1)
            headers["Range"] = "bytes={}-{}".format(offset, offset+99)
            response = self.request(nozomi_url, headers=headers)

            for gallery_id in decode_nozomi(response.content):
                gallery_url = "{}/galleries/{}.html".format(
                    self.root, gallery_id)
                yield Message.Queue, gallery_url, data

            offset += 100
            if total is None:
                total = text.parse_int(
                    response.headers["content-range"].rpartition("/")[2])
            if offset >= total:
                return


class HitomiSearchExtractor(HitomiExtractor):
    """Extractor for galleries from multiple tag searches on hitomi.la"""
    subcategory = "search"
    pattern = r"(?:https?://)?hitomi\.la/search\.html\?([^/?#]+)"
    example = "https://hitomi.la/search.html?QUERY"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match.group(1)
        self.tags = text.unquote(self.query)

    def items(self):
        data = {
            "_extractor": HitomiGalleryExtractor,
            "search_tags": self.tags,
        }
        results = [self.get_nozomi_items(tag) for tag in self.tags.split(" ")]
        intersects = set.intersection(*results)

        for gallery_id in sorted(intersects, reverse=True):
            gallery_url = "{}/galleries/{}.html".format(
                self.root, gallery_id)
            yield Message.Queue, gallery_url, data

    def get_nozomi_items(self, full_tag):
        area, tag, language = self.get_nozomi_args(full_tag)

        if area:
            nozomi_url = "https://ltn.{}/n/{}/{}-{}.nozomi".format(
                self.domain, area, tag, language)
        else:
            nozomi_url = "https://ltn.{}/n/{}-{}.nozomi".format(
                self.domain, tag, language)

        headers = {
            "Origin": self.root,
            "Cache-Control": "max-age=0",
            "Referer": "{}/search.html?{}".format(self.root, self.query),
        }

        response = self.request(nozomi_url, headers=headers)
        return set(decode_nozomi(response.content))

    def get_nozomi_args(self, query):
        ns, _, tag = query.strip().partition(":")
        area = ns
        language = "all"

        if ns == "female" or ns == "male":
            area = "tag"
            tag = query
        elif ns == "language":
            area = None
            language = tag
            tag = "index"

        return area, tag.replace("_", " "), language


@memcache(maxage=1800)
def _parse_gg(extr):
    page = extr.request("https://ltn.gold-usergeneratedcontent.net/gg.js").text

    m = {}

    keys = []
    for match in re.finditer(
            r"case\s+(\d+):(?:\s*o\s*=\s*(\d+))?", page):
        key, value = match.groups()
        keys.append(int(key))

        if value:
            value = int(value)
            for key in keys:
                m[key] = value
            keys.clear()

    for match in re.finditer(
            r"if\s+\(g\s*===?\s*(\d+)\)[\s{]*o\s*=\s*(\d+)", page):
        m[int(match.group(1))] = int(match.group(2))

    d = re.search(r"(?:var\s|default:)\s*o\s*=\s*(\d+)", page)
    b = re.search(r"b:\s*[\"'](.+)[\"']", page)

    return m, b.group(1).strip("/"), int(d.group(1)) if d else 0
