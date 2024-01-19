# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://Hreads.net/"""

import re
from .common import MangaExtractor, ChapterExtractor
from .. import text


BASE_PATTERN = r"(?:https?://)?hreads\.net"


class HreadsBase:
    """Base class for Hreads extractors"""

    category = "hreads"
    root = "https://hreads.net/"

    def get_title(self, page):
        """Gets the title of the manga"""
        title = text.extr(page, "<title>", "</title>")
        title = text.unescape(title).strip()
        match = re.search(
            r"(?:Read )?([\w\d ]+?)(?:(?: - Chapter [\d.]+)? - Hreads)",
            title,
        )
        if match:
            title = match.group(1)
        return title


class HreadsChapterExtractor(HreadsBase, ChapterExtractor):
    """Extractor for manga chapters from Hreads.net"""

    subcategory = "chapter"
    directory_fmt = (
        "{category}",
        "{manga}",
        "Chapter-{chapter:03}{chapter_minor}",
    )
    archive_fmt = "{chapter:03}{chapter_minor}_{page}"
    pattern = BASE_PATTERN + r"/comic/([\w\d-]+)\/chapter-(\d+-[\d+]|\d+)/?"
    example = "https://hreads.net/comics/sex-stopwatch/chapter-1/"

    def __init__(self, match):
        url = match.group(0)
        self.gid, self.chapter = match.groups()
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        chapter, sep, minor = self.chapter.partition("-")

        data = {
            "manga": self.get_title(page),
            "manga_id": self.gid,
            "chapter": text.parse_int(chapter),
            "chapter_id": f"{self.gid}-chapter-{self.chapter}",
            "chapter_minor": sep + minor,
        }
        return data

    def images(self, page):
        images = []
        first_img = text.extract(page, 'src="https://cdn.hreads.net', '"')
        images.append((f"https://cdn.hreads.net{first_img[0].strip()}", None))

        for url in text.extract_iter(page, 'data-src="', '"'):
            images.append((url.strip(), None))
        return images


class HreadsMangaExtractor(HreadsBase, MangaExtractor):
    """Extractor for manga from Hreads.net"""

    subcategory = "manga"
    chapterclass = HreadsChapterExtractor
    pattern = BASE_PATTERN + r"/comic/([\w\d-]+)/?$"
    example = "https://hreads.net/comics/sex-stopwatch"

    def __init__(self, match):
        url, self.gid = match.group(0), match.group(1)
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        chapters = set()
        print("Chapter extraction")
        for chapter_id in text.extract_iter(
            page, f'<a href="https://hreads.net/comic/{self.gid}/chapter', '/"'
        ):
            chapters.add(f"chapter{chapter_id}")

        title = self.get_title(page)
        results = []

        for chapter_id in chapters:
            chapter, sep, minor = chapter_id[8:].partition("-")
            results.append(
                (
                    f"{self.root}comic/{self.gid}/{chapter_id}",
                    {
                        "manga_id": self.gid,
                        "chapter_id": chapter_id,
                        "chapter": text.parse_int(chapter),
                        "chapter_minor": sep + minor,
                        "manga": title,
                        "lang": "en",
                        "language": "English",
                    },
                )
            )
        print(results)
        return results
