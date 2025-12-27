# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangalib.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, exception
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangalib\.me"


class MangalibBase():
    """Base class for mangalib extractors"""
    category = "mangalib"
    root = "https://mangalib.me"

    def slug_to_name(self, slug):
        try:
            return slug.split("--", 1)[-1].replace("-", " ").strip()
        except Exception:
            return slug


class MangalibChapterExtractor(MangalibBase, ChapterExtractor):
    """Extractor for mangalib manga chapters"""
    example = "https://mangalib.me/ru/123--TITLE/read/v1/c1"
    pattern = rf"{BASE_PATTERN}/ru/([^/?#]+)/read/v(\d+)/c(\d+(?:\.\d+)?)(.*)"

    def __init__(self, match):
        ChapterExtractor.__init__(self, match, False)
        slug, vol, chstr, tail = self.groups
        self.api_url = (
            f"https://api.cdnlibs.org/api/manga/{slug}/chapter" +
            f"?number={chstr}&volume={vol}"
        )
        m = text.re(r"bid=(\d+)").search(tail)
        self.api_url += f"&branch_id={m.group(1)}" if m is not None else ""

    def metadata(self, _):
        slug, vol, chstr, _ = self.groups
        resp = _api_call(self)

        number, sep, minor = chstr.partition(".")
        teams_joined = ",".join([team["name"] for team in resp["teams"]])
        return {
            "manga"        : self.slug_to_name(slug),
            "manga_slug"   : slug,
            "volume"       : text.parse_int(vol),
            "chapter"      : text.parse_int(number),
            "chapter_minor": sep + minor,
            "title"        : resp["name"] or "",
            "lang"         : "ru",
            "language"     : "Russian",
            "teams"        : teams_joined,
        }

    def images(self, _):
        resp = _api_call(self)
        base = "https://img3.mixlib.me"
        return [(base + item["url"], None) for item in resp["pages"]]


class MangalibMangaExtractor(MangalibBase, MangaExtractor):
    """Extractor for mangalib manga"""
    chapterclass = MangalibChapterExtractor
    example = "https://mangalib.me/ru/manga/123--TITLE"
    pattern = (rf"{BASE_PATTERN}/ru/manga/([^/?#]+)")
    reverse = False

    def __init__(self, match):
        MangaExtractor.__init__(self, match, False)
        self.api_url = (
            "https://api.cdnlibs.org/api/manga/" +
            f"{self.groups[0]}/chapters"
        )

    def chapters(self, _):
        slug = self.groups[0]
        data = _api_call(self)

        if "toast" in data:
            raise exception.AbortExtraction(data["toast"]["message"])

        results = []
        for chapter in data:
            url = (
                f"{self.root}/ru/{slug}/read/" +
                f"v{chapter['volume']}/c{chapter['number']}"
            )
            number, sep, minor = chapter["number"].partition(".")
            # every chapter can have many translations by different teams,
            # which is represented by branches (I hardcoded first branch)
            for branch in chapter["branches"][:1]:
                branch_id = branch["branch_id"]
                teams = ",".join([team["name"] for team in branch["teams"]])
                data = {
                    "manga"        : self.slug_to_name(slug),
                    "manga_slug"   : slug,
                    "volume"       : text.parse_int(chapter["volume"]),
                    "chapter"      : text.parse_int(number),
                    "chapter_minor": sep + minor,
                    "title"        : chapter["name"] or "",
                    "lang"         : "ru",
                    "language"     : "Russian",
                    "teams"        : teams,
                }
                results.append((url + f"?bid={branch_id}", data))

        return results


@memcache(keyarg=0)
def _api_call(extr):
    return extr.request_json(extr.api_url)["data"]
