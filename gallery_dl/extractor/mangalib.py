# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangalib.me/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util, exception

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
        slug, vol, chstr, tail = match.groups()
        url = f"https://api.cdnlibs.org/api/manga/{slug}/chapter?number={chstr}&volume={vol}"
        m = text.re(r"bid=(\d+)").search(tail)
        url += f"&branch_id={m.group(1)}" if m is not None else ""
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        slug, vol, chstr, _ = self.groups
        resp = util.json_loads(page)["data"]

        number, sep, minor = chstr.partition(".")
        return {
            "manga"        : self.slug_to_name(slug),
            "manga_slug"   : slug,
            "volume"       : text.parse_int(vol),
            "chapter"      : text.parse_int(number),
            "chapter_minor": sep + minor,
            "title"        : resp["name"] or "",
            "lang"         : "ru",
            "language"     : "Russian",
            "teams"        : ",".join([team["name"] for team in resp["teams"]]),
        }

    def images(self, page):
        resp = util.json_loads(page)["data"]
        base = "https://img3.mixlib.me"
        return [(base + item["url"], None) for item in resp["pages"]]


class MangalibMangaExtractor(MangalibBase, MangaExtractor):
    """Extractor for mangalib manga"""
    chapterclass = MangalibChapterExtractor
    example = "https://mangalib.me/ru/manga/123--TITLE"
    pattern = (rf"{BASE_PATTERN}/ru/manga/([^/?#]+)")
    reverse = False

    def chapters(self, _):
        slug = self.groups[0]

        api_url = f"https://api.cdnlibs.org/api/manga/{slug}/chapters"
        data = self.request_json(api_url, fatal=False)["data"]
        if "toast" in data:
            raise exception.AbortExtraction(data["toast"]["message"])

        results = []
        for chapter in data:
            url = f"{self.root}/ru/{slug}/read/v{chapter['volume']}/c{chapter['number']}"
            number, sep, minor = chapter["number"].partition(".")
            # every chapter can have many translations by different teams, which is represented by branches
            # (hardcoded first branch)
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