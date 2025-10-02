# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangareader.to/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangareader\.to"


class MangareaderBase():
    """Base class for mangareader extractors"""
    category = "mangareader"
    root = "https://mangareader.to"


class MangareaderChapterExtractor(MangareaderBase, ChapterExtractor):
    """Extractor for mangareader manga chapters"""
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}{chapter:?c//>03}{chapter_minor:?//}{title:?: //}")
    filename_fmt = (
        "{manga}{volume:?_v//>02}{chapter:?_c//>03}{chapter_minor:?//}_"
        "{page:>03}.{extension}")
    archive_fmt = (
        "{manga_id}_{chapter_id}_{page}")
    pattern = (rf"{BASE_PATTERN}/read/([\w-]+-\d+)/([^/?#]+)"
               rf"/(chapter|volume)-(\d+[^/?#]*)")
    example = "https://mangareader.to/read/MANGA-123/LANG/chapter-123"

    def metadata(self, _):
        path, lang, type, chstr = self.groups

        settings = util.json_dumps({
            "readingMode"     : "vertical",
            "readingDirection": "rtl",
            "quality"         : "high",
        })
        self.cookies.set("mr_settings", settings, domain="mangareader.to")

        url = f"{self.root}/read/{path}/{lang}/{type}-{chstr}"
        page = self.request(url).text
        self.cid = cid = text.extr(page, 'data-reading-id="', '"')

        manga = _manga_info(self, path)
        return {
            **manga,
            **manga[f"_{type}s"][lang][chstr],
            "chapter_id": text.parse_int(cid),
        }

    def images(self, page):
        key = "chap" if self.groups[2] == "chapter" else "vol"
        url = f"{self.root}/ajax/image/list/{key}/{self.cid}"
        params = {
            "mode"       : "vertical,",
            "quality"    : "high,",
            "hozPageSize": "1,",
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest"  : "empty",
            "Sec-Fetch-Mode"  : "cors",
            "Sec-Fetch-Site"  : "same-origin",
        }
        html = self.request_json(url, params=params, headers=headers)["html"]

        return [
            (url, None)
            for url in text.extract_iter(html, 'data-url="', '"')
        ]


class MangareaderMangaExtractor(MangareaderBase, MangaExtractor):
    """Extractor for mangareader manga"""
    chapterclass = MangareaderChapterExtractor
    pattern = rf"{BASE_PATTERN}/([\w-]+-\d+)"
    example = "https://mangareader.to/MANGA-123"

    def chapters(self, page):
        manga = _manga_info(self, self.groups[0])
        lang = self.config("lang") or "en"

        return [
            (info["chapter_url"], {**manga, **info})
            for info in manga["_chapters"][lang].values()
        ]


@memcache(keyarg=1)
def _manga_info(self, manga_path):
    url = f"{self.root}/{manga_path}"
    html = self.request(url).text

    slug, _, mid = manga_path.rpartition("-")
    extr = text.extract_from(html)
    url = extr('property="og:url" content="', '"')
    manga = {
        "manga_url": url,
        "manga_slug": url.rpartition("/")[2].rpartition("-")[0],
        "manga_id": text.parse_int(mid),
        "manga": text.unescape(extr('class="manga-name">', "<")),
        "manga_alt": text.unescape(extr('class="manga-name-or">', "<")),
        "tags": text.split_html(extr('class="genres">', "</div>")),
        "type": text.remove_html(extr('>Type:', "</div>")),
        "status": text.remove_html(extr('>Status:', "</div>")),
        "author": text.split_html(extr('>Authors:', "</div>"))[0::2],
        "published": text.remove_html(extr('>Published:', "</div>")),
        "score": text.parse_float(text.remove_html(extr(
            '>Score:', "</div>"))),
        "views": text.parse_int(text.remove_html(extr(
            '>Views:', "</div>")).replace(",", "")),
    }

    base = self.root

    # extract all chapters
    html = extr('class="chapters-list-ul">', "    </div>")
    manga["_chapters"] = chapters = {}
    for group in text.extract_iter(html, "<ul", "</ul>"):
        lang = text.extr(group, ' id="', '-chapters"')

        chapters[lang] = current = {}
        lang = lang.partition("-")[0]
        for ch in text.extract_iter(group, "<li ", "</li>"):
            path = text.extr(ch, 'href="', '"')
            chap = text.extr(ch, 'data-number="', '"')
            name = text.unescape(text.extr(ch, 'class="name">', "<"))

            chapter, sep, minor = chap.partition(".")
            current[chap] = {
                "title"         : name.partition(":")[2].strip(),
                "chapter"       : text.parse_int(chapter),
                "chapter_minor" : f"{sep}{minor}",
                "chapter_string": chap,
                "chapter_url"   : f"{base}{path}",
                "lang"          : lang,
            }

    # extract all volumes
    html = extr('class="volume-list-ul">', "</section>")
    manga["_volumes"] = volumes = {}
    for group in html.split('<div class="manga_list-wrap')[1:]:
        lang = text.extr(group, ' id="', '-volumes"')

        volumes[lang] = current = {}
        lang = lang.partition("-")[0]
        for vol in text.extract_iter(group, 'class="item">', "</div>"):
            path = text.extr(vol, 'href="', '"')
            voln = text.extr(vol, 'tick-vol">', '<').rpartition(" ")[2]

            current[voln] = {
                "volume"        : text.parse_int(voln),
                "volume_cover"  : text.extr(vol, ' src="', '"'),
                "chapter"       : 0,
                "chapter_minor" : "",
                "chapter_string": voln,
                "chapter_url"   : f"{base}{path}",
                "lang"          : lang,
            }

    # extract remaining metadata
    manga["description"] = text.unescape(extr(
        'class="description-modal">', "</div>")).strip()

    return manga
