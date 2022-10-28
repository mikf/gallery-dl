# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
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
import json
import re


class HitomiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from hitomi.la"""
    category = "hitomi"
    root = "https://hitomi.la"
    pattern = (r"(?:https?://)?hitomi\.la"
               r"/(?:manga|doujinshi|cg|gamecg|galleries|reader)"
               r"/(?:[^/?#]+-)?(\d+)")
    test = (
        ("https://hitomi.la/galleries/867789.html", {
            "pattern": r"https://[a-c]a\.hitomi\.la/webp/\d+/\d+"
                       r"/[0-9a-f]{64}\.webp",
            "keyword": "86af5371f38117a07407f11af689bdd460b09710",
            "count": 16,
        }),
        # download test
        ("https://hitomi.la/galleries/1401410.html", {
            "range": "1",
            "content": "d75d5a3d1302a48469016b20e53c26b714d17745",
        }),
        # Game CG with scenes (#321)
        ("https://hitomi.la/galleries/733697.html", {
            "count": 210,
        }),
        # fallback for galleries only available through /reader/ URLs
        ("https://hitomi.la/galleries/1045954.html", {
            "count": 1413,
        }),
        # gallery with "broken" redirect
        ("https://hitomi.la/cg/scathacha-sama-okuchi-ecchi-1291900.html", {
            "count": 10,
            "options": (("format", "original"),),
            "pattern": r"https://[a-c]b\.hitomi\.la/images/\d+/\d+"
                       r"/[0-9a-f]{64}\.jpg",
        }),
        # no tags
        ("https://hitomi.la/cg/1615823.html", {
            "count": 22,
            "options": (("format", "avif"),),
            "pattern": r"https://[a-c]a\.hitomi\.la/avif/\d+/\d+"
                       r"/[0-9a-f]{64}\.avif",
        }),
        ("https://hitomi.la/manga/amazon-no-hiyaku-867789.html"),
        ("https://hitomi.la/manga/867789.html"),
        ("https://hitomi.la/doujinshi/867789.html"),
        ("https://hitomi.la/cg/867789.html"),
        ("https://hitomi.la/gamecg/867789.html"),
        ("https://hitomi.la/reader/867789.html"),
    )

    def __init__(self, match):
        gid = match.group(1)
        url = "https://ltn.hitomi.la/galleries/{}.js".format(gid)
        GalleryExtractor.__init__(self, match, url)
        self.info = None
        self.session.headers["Referer"] = "{}/reader/{}.html".format(
            self.root, gid)

    def metadata(self, page):
        self.info = info = json.loads(page.partition("=")[2])
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
        # see https://ltn.hitomi.la/gg.js
        gg_m, gg_b, gg_default = _parse_gg(self)

        fmt = self.config("format") or "webp"
        if fmt == "original":
            subdomain, fmt, ext, check = "b", "images", None, False
        else:
            subdomain, ext, check = "a", fmt, True

        result = []
        for image in self.info["files"]:
            if check:
                if not image.get("has" + fmt):
                    fmt = ext = "webp"
                check = False
            ihash = image["hash"]
            idata = text.nameext_from_url(image["name"])
            if ext:
                idata["extension"] = ext

            # see https://ltn.hitomi.la/common.js
            inum = int(ihash[-1] + ihash[-3:-1], 16)
            url = "https://{}{}.hitomi.la/{}/{}/{}/{}.{}".format(
                chr(97 + gg_m.get(inum, gg_default)),
                subdomain, fmt, gg_b, inum, ihash, idata["extension"],
            )
            result.append((url, idata))
        return result


class HitomiTagExtractor(Extractor):
    """Extractor for galleries from tag searches on hitomi.la"""
    category = "hitomi"
    subcategory = "tag"
    root = "https://hitomi.la"
    pattern = (r"(?:https?://)?hitomi\.la/"
               r"(tag|artist|group|series|type|character)/"
               r"([^/?#]+)\.html")
    test = (
        ("https://hitomi.la/tag/screenshots-japanese.html", {
            "pattern": HitomiGalleryExtractor.pattern,
            "count": ">= 35",
        }),
        ("https://hitomi.la/artist/a1-all-1.html"),
        ("https://hitomi.la/group/initial%2Dg-all-1.html"),
        ("https://hitomi.la/series/amnesia-all-1.html"),
        ("https://hitomi.la/type/doujinshi-all-1.html"),
        ("https://hitomi.la/character/a2-all-1.html"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.type, self.tag = match.groups()

        tag, _, num = self.tag.rpartition("-")
        if num.isdecimal():
            self.tag = tag

    def items(self):
        data = {"_extractor": HitomiGalleryExtractor}
        nozomi_url = "https://ltn.hitomi.la/{}/{}.nozomi".format(
            self.type, self.tag)
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


@memcache(maxage=1800)
def _parse_gg(extr):
    page = extr.request("https://ltn.hitomi.la/gg.js").text

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

    return m, b.group(1).strip("/"), int(d.group(1)) if d else 1
