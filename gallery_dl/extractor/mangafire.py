# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangafire.to/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, exception
from ..cache import memcache
import binascii

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangafire\.to"


class MangafireBase():
    """Base class for mangafire extractors"""
    category = "mangafire"
    root = "https://mangafire.to"


class MangafireChapterExtractor(MangafireBase, ChapterExtractor):
    """Extractor for mangafire manga chapters"""
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}{chapter:?c//>03}{chapter_minor:?//}{title:?: //}")
    filename_fmt = (
        "{manga}{volume:?_v//>02}{chapter:?_c//>03}{chapter_minor:?//}_"
        "{page:>03}.{extension}")
    archive_fmt = (
        "{manga_id}_{chapter_id}_{page}")
    pattern = (BASE_PATTERN + r"/read/([\w-]+\.(\w+))/([\w-]+)"
               r"/((chapter|volume)-\d+(?:\D.*)?)")
    example = "https://mangafire.to/read/MANGA.ID/LANG/chapter-123"

    def metadata(self, _):
        manga_path, manga_id, lang, chapter_info, self.type = self.groups

        try:
            chapters = _manga_chapters(self, (manga_id, self.type, lang))
            anchor = chapters[chapter_info]
        except KeyError:
            raise exception.NotFoundError("chapter")
        self.chapter_id = text.extr(anchor, 'data-id="', '"')

        return {
            **_manga_info(self, manga_path),
            **_chapter_info(anchor),
        }

    def images(self, page):
        url = f"{self.root}/ajax/read/{self.type}/{self.chapter_id}"
        params = {"vrf": generate_VRF(f"{self.type}@{self.chapter_id}")}
        headers = {"x-requested-with": "XMLHttpRequest"}
        data = self.request_json(url, params=params, headers=headers)

        return [
            (image[0], None)
            for image in data["result"]["images"]
        ]


class MangafireMangaExtractor(MangafireBase, MangaExtractor):
    """Extractor for mangafire manga"""
    chapterclass = MangafireChapterExtractor
    pattern = BASE_PATTERN + r"/manga/([\w-]+)\.(\w+)"
    example = "https://mangafire.to/manga/MANGA.ID"

    def chapters(self, page):
        manga_slug, manga_id = self.groups
        lang = self.config("lang") or "en"

        manga = _manga_info(self, f"{manga_slug}.{manga_id}")
        chapters = _manga_chapters(self, (manga_id, "chapter", lang))

        return [
            (self.root + text.extr(anchor, 'href="', '"'), {
                **manga,
                **_chapter_info(anchor),
            })
            for anchor in chapters.values()
        ]


@memcache(keyarg=1)
def _manga_info(self, manga_path, page=None):
    if page is None:
        url = f"{self.root}/manga/{manga_path}"
        page = self.request(url).text
    slug, _, mid = manga_path.rpartition(".")

    extr = text.extract_from(page)
    manga = {
        "cover": text.extr(extr(
            'class="poster">', '</div>'), 'src="', '"'),
        "status": extr("<p>", "<").replace("_", " ").title(),
        "manga"     : text.unescape(extr(
            'itemprop="name">', "<")),
        "manga_id": mid,
        "manga_slug": slug,
        "manga_titles": text.unescape(extr(
            "<h6>", "<")).split("; "),
        "type": text.remove_html(extr(
            'class="min-info">', "</a>")),
        "author": text.unescape(text.remove_html(extr(
            "<span>Author:</span>", "</div>"))).split(" , "),
        "published": text.remove_html(extr(
            "<span>Published:</span>", "</div>")),
        "tags": text.split_html(extr(
            "<span>Genres:</span>", "</div>"))[::2],
        "publisher": text.unescape(text.remove_html(extr(
            "<span>Mangazines:</span>", "</div>"))).split(" , "),
        "score": text.parse_float(text.remove_html(extr(
            'class="score">', " / "))),
        "description": text.remove_html(extr(
            'id="synopsis">', "<script>")),
    }

    if len(lst := manga["author"]) == 1 and not lst[0]:
        manga["author"] = ()
    if len(lst := manga["publisher"]) == 1 and not lst[0]:
        manga["publisher"] = ()

    return manga


@memcache(keyarg=1)
def _manga_chapters(self, manga_info):
    manga_id, type, lang = manga_info
    url = f"{self.root}/ajax/read/{manga_id}/{type}/{lang}"
    params = {"vrf": generate_VRF(f"{manga_id}@{type}@{lang}")}
    headers = {"x-requested-with": "XMLHttpRequest"}
    data = self.request_json(url, params=params, headers=headers)

    needle = f"{manga_id}/{lang}/"
    return {
        text.extr(anchor, needle, '"'): anchor
        for anchor in text.extract_iter(data["result"]["html"], "<a ", ">")
    }


@memcache(keyarg=0)
def _chapter_info(info):
    _, lang, chapter_info = text.extr(info, 'href="', '"').rsplit("/", 2)

    if chapter_info.startswith("vol"):
        volume = text.extr(info, 'data-number="', '"')
        volume_id = text.parse_int(text.extr(info, 'data-id="', '"'))
        return {
            "volume"        : text.parse_int(volume),
            "volume_id"     : volume_id,
            "chapter"       : 0,
            "chapter_minor" : "",
            "chapter_string": chapter_info,
            "chapter_id"    : volume_id,
            "title"         : text.unescape(text.extr(info, 'title="', '"')),
            "lang"          : lang,
        }

    chapter, sep, minor = text.extr(info, 'data-number="', '"').partition(".")
    return {
        "chapter"       : text.parse_int(chapter),
        "chapter_minor" : sep + minor,
        "chapter_string": chapter_info,
        "chapter_id"    : text.parse_int(text.extr(info, 'data-id="', '"')),
        "title"         : text.unescape(text.extr(info, 'title="', '"')),
        "lang"          : lang,
    }


###############################################################################
# VRF generation utils
#
# adapted from dazedcat19/FMD2
# https://github.com/dazedcat19/FMD2/blob/master/lua/modules/MangaFire.lua

def generate_VRF(input):
    input = text.quote(input).encode()

    for key_b64, seed_b64, prefix_b64, schedule in (
        (key_l, seed_A, prefix_O, schedule_c),
        (key_g, seed_V, prefix_v, schedule_y),
        (key_B, seed_N, prefix_L, schedule_b),
        (key_m, seed_P, prefix_p, schedule_j),
        (key_F, seed_k, prefix_W, schedule_e),
    ):
        input = transform(
            rc4(binascii.a2b_base64(key_b64), input),
            binascii.a2b_base64(seed_b64),
            binascii.a2b_base64(prefix_b64),
            schedule,
        )

    return binascii.b2a_base64(bytes(input), newline=False).rstrip(
        b"=").replace(b"+", b"-").replace(b"/", b"_")


def transform(input, seed, prefix, schedule):
    prefix_len = len(prefix)

    out = []
    for idx, c in enumerate(input):
        if idx < prefix_len:
            out.append(prefix[idx] or 0)
        out.append(schedule[idx % 10]((c ^ seed[idx % 32]) & 255) & 255)
    return out


def rc4(key, input):
    lkey = len(key)

    j = 0
    s = list(range(256))
    for i in range(256):
        j = (j + s[i] + key[i % lkey]) & 255
        s[i], s[j] = s[j], s[i]

    out = []
    i = j = 0
    for c in input:
        i = (i + 1) & 255
        j = (j + s[i]) & 255
        s[i], s[j] = s[j], s[i]
        k = s[(s[i] + s[j]) & 255]
        out.append(c ^ k)
    return out


def add8(n):
    return lambda c: (c + n) & 255


def sub8(n):
    return lambda c: (c - n + 256) & 255


def xor8(n):
    return lambda c: (c ^ n) & 255


def rotl8(n):
    return lambda c: ((c << n) | (c >> (8 - n))) & 255


def rotr8(n):
    return lambda c: ((c >> n) | (c << (8 - n))) & 255


schedule_c = (
    sub8(223), rotr8(4), rotr8(4), add8(234), rotr8(7),
    rotr8(2), rotr8(7), sub8(223), rotr8(7), rotr8(6),
)
schedule_y = (
    add8(19), rotr8(7), add8(19), rotr8(6), add8(19),
    rotr8(1), add8(19), rotr8(6), rotr8(7), rotr8(4),
)
schedule_b = (
    sub8(223), rotr8(1), add8(19), sub8(223), rotl8(2),
    sub8(223), add8(19), rotl8(1), rotl8(2), rotl8(1),
)
schedule_j = (
    add8(19), rotl8(1), rotl8(1), rotr8(1), add8(234),
    rotl8(1), sub8(223), rotl8(6), rotl8(4), rotl8(1),
)
schedule_e = (
    rotr8(1), rotl8(1), rotl8(6), rotr8(1), rotl8(2),
    rotr8(4), rotl8(1), rotl8(1), sub8(223), rotl8(2),
)


key_l = "FgxyJUQDPUGSzwbAq/ToWn4/e8jYzvabE+dLMb1XU1o="
key_g = "CQx3CLwswJAnM1VxOqX+y+f3eUns03ulxv8Z+0gUyik="
key_B = "fAS+otFLkKsKAJzu3yU+rGOlbbFVq+u+LaS6+s1eCJs="
key_m = "Oy45fQVK9kq9019+VysXVlz1F9S1YwYKgXyzGlZrijo="
key_F = "aoDIdXezm2l3HrcnQdkPJTDT8+W6mcl2/02ewBHfPzg="

seed_A = "yH6MXnMEcDVWO/9a6P9W92BAh1eRLVFxFlWTHUqQ474="
seed_V = "RK7y4dZ0azs9Uqz+bbFB46Bx2K9EHg74ndxknY9uknA="
seed_N = "rqr9HeTQOg8TlFiIGZpJaxcvAaKHwMwrkqojJCpcvoc="
seed_P = "/4GPpmZXYpn5RpkP7FC/dt8SXz7W30nUZTe8wb+3xmU="
seed_k = "wsSGSBXKWA9q1oDJpjtJddVxH+evCfL5SO9HZnUDFU8="

prefix_O = "l9PavRg="
prefix_v = "Ml2v7ag1Jg=="
prefix_L = "i/Va0UxrbMo="
prefix_p = "WFjKAHGEkQM="
prefix_W = "5Rr27rWd"
