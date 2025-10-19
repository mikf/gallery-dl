# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
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


class HitomiExtractor(Extractor):
    """Base class for hitomi extractors"""
    category = "hitomi"
    root = "https://hitomi.la"
    domain = "gold-usergeneratedcontent.net"

    def load_nozomi(self, query, language="all", headers=None):
        ns, _, tag = query.strip().partition(":")

        if ns == "female" or ns == "male":
            ns = "tag/"
            tag = query
        elif ns == "language":
            ns = ""
            language = tag
            tag = "index"
        else:
            ns = f"{ns}/"

        url = (f"https://ltn.{self.domain}/n/{ns}"
               f"/{tag.replace('_', ' ')}-{language}.nozomi")
        if headers is None:
            headers = {}
        headers["Origin"] = self.root
        headers["Referer"] = f"{self.root}/"
        return decode_nozomi(self.request(url, headers=headers).content)


class HitomiGalleryExtractor(HitomiExtractor, GalleryExtractor):
    """Extractor for hitomi.la galleries"""
    pattern = (r"(?:https?://)?hitomi\.la"
               r"/(?:manga|doujinshi|cg|gamecg|imageset|galleries|reader)"
               r"/(?:[^/?#]+-)?(\d+)")
    example = "https://hitomi.la/manga/TITLE-867789.html"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match, False)
        self.gid = gid = self.groups[0]
        self.page_url = f"https://ltn.{self.domain}/galleries/{gid}.js"

    def _init(self):
        self.session.headers["Referer"] = f"{self.root}/reader/{self.gid}.html"

    def metadata(self, page):
        self.info = info = util.json_loads(page.partition("=")[2])
        iget = info.get

        if language := iget("language"):
            language = language.capitalize()

        if date := iget("date"):
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
            "date"      : self.parse_datetime_iso(date),
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

        results = []
        for image in self.info["files"]:
            if check:
                ext = fmt if image.get("has" + fmt) else "webp"
            ihash = image["hash"]
            idata = text.nameext_from_url(image["name"])
            idata["extension_original"] = idata["extension"]
            idata["extension"] = ext

            # https://ltn.gold-usergeneratedcontent.net/common.js
            inum = int(ihash[-1] + ihash[-3:-1], 16)
            url = (f"https://{ext[0]}{gg_m.get(inum, gg_default) + 1}."
                   f"{self.domain}/{gg_b}/{inum}/{ihash}.{ext}")
            results.append((url, idata))
        return results


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
        nozomi_url = f"https://ltn.{self.domain}/{self.type}/{self.tag}.nozomi"
        headers = {
            "Origin": self.root,
            "Cache-Control": "max-age=0",
        }

        offset = 0
        total = None
        while True:
            headers["Referer"] = (f"{self.root}/{self.type}/{self.tag}.html"
                                  f"?page={offset // 100 + 1}")
            headers["Range"] = f"bytes={offset}-{offset + 99}"
            response = self.request(nozomi_url, headers=headers)

            for gallery_id in decode_nozomi(response.content):
                gallery_url = f"{self.root}/galleries/{gallery_id}.html"
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
        nozomi_url = (f"https://ltn.{self.domain}"
                      f"/{self.tag}-{self.language}.nozomi")
        headers = {
            "Origin": self.root,
            "Cache-Control": "max-age=0",
        }

        offset = 0
        total = None
        while True:
            headers["Referer"] = (f"{self.root}/{self.tag}-{self.language}"
                                  f".html?page={offset // 100 + 1}")
            headers["Range"] = f"bytes={offset}-{offset + 99}"
            response = self.request(nozomi_url, headers=headers)

            for gallery_id in decode_nozomi(response.content):
                gallery_url = f"{self.root}/galleries/{gallery_id}.html"
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
    pattern = r"(?:https?://)?hitomi\.la/search\.html\?([^#]+)"
    example = "https://hitomi.la/search.html?QUERY"

    def items(self):
        tags = text.unquote(self.groups[0])

        data = {
            "_extractor": HitomiGalleryExtractor,
            "search_tags": tags,
        }

        for gallery_id in self.gallery_ids(tags):
            gallery_url = f"{self.root}/galleries/{gallery_id}.html"
            yield Message.Queue, gallery_url, data

    def gallery_ids(self, tags):
        result = None
        positive = []
        negative = []

        for tag in tags.split():
            if tag[0] == "-":
                negative.append(tag[1:])
            else:
                positive.append(tag)

        for tag in positive:
            ids = self.load_nozomi(tag)
            if result is None:
                result = set(ids)
            else:
                result.intersection_update(ids)

        if result is None:
            #  result = set(self.load_nozomi("index"))
            result = set(self.load_nozomi("language:all"))
        for tag in negative:
            result.difference_update(self.load_nozomi(tag))

        return sorted(result, reverse=True) if result else ()


@memcache(maxage=1800)
def _parse_gg(extr):
    page = extr.request("https://ltn.gold-usergeneratedcontent.net/gg.js").text

    m = {}

    keys = []
    for match in util.re_compile(
            r"case\s+(\d+):(?:\s*o\s*=\s*(\d+))?").finditer(page):
        key, value = match.groups()
        keys.append(int(key))

        if value:
            value = int(value)
            for key in keys:
                m[key] = value
            keys.clear()

    for match in util.re_compile(
            r"if\s+\(g\s*===?\s*(\d+)\)[\s{]*o\s*=\s*(\d+)").finditer(page):
        m[int(match[1])] = int(match[2])

    d = util.re_compile(r"(?:var\s|default:)\s*o\s*=\s*(\d+)").search(page)
    b = util.re_compile(r"b:\s*[\"'](.+)[\"']").search(page)

    return m, b[1].strip("/"), int(d[1]) if d else 0
