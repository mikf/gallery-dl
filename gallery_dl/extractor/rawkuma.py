# -*- coding: utf-8 -*-

"""Extractors for https://rawkuma.com/"""

from .common import MangaExtractor, ChapterExtractor
from .. import text, util
import re

BASE_PATTERN = r"(?:https?://)?rawkuma\.com"


class RawkumaBase():
    """Base class for rawkuma extractors"""
    category = "rawkuma"
    root = "https://rawkuma.com"

    def get_title(self, page):
        title = text.extr(page, 'property="og:title" content="', '"')
        title = text.unescape(title).strip()
        m = re.search(
            r"(.+) (?:Manga|Chapter \d+) (?:Raw - Rawkuma)", title)
        if m:
            title = m.group(1)
        return title


class RawkumaChapterExtractor(RawkumaBase, ChapterExtractor):
    """Extractor for manga chapters from rawkuma.com"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = BASE_PATTERN + r"/([\w\d-]+)-chapter-(\d+)"
    example = "https://rawkuma.com/ID-chapter-1"

    def __init__(self, match):
        url = match.group(0)
        self.gid, self.chapter = match.groups()
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = self.get_title(page)
        chapter, sep, minor = self.chapter.partition(".")
        return {
            "manga": title,
            "manga_id": self.gid,
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": "%s-chapter-%s" % (self.gid, self.chapter),
        }

    def images(self, page):
        results = []
        pos = 0
        json, pos = text.extract(page, "<script>ts_reader.run(",
                                 ");</script>", pos)
        json_data = util.json_loads(json)
        source = json_data.get("sources", [{}])[0]
        images = source.get("images", [])

        for url in images:
            results.append((url, None))

        return results


class RawkumaMangaExtractor(RawkumaBase, MangaExtractor):
    """Extractor for manga from rawkuma.com"""
    chapterclass = RawkumaChapterExtractor
    pattern = BASE_PATTERN + r"/manga/([\w\d-]+)"
    example = "https://rawkuma.com/manga/ID"

    def __init__(self, match):
        url, self.gid = match.group(0), match.group(1)
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        results = []
        pos = 0
        title = self.get_title(page)

        while True:
            chapter_id, pos = \
                text.extract(page, '<div class="eph-num">\n'
                             '<a href="https://rawkuma.com/',
                             '/"', pos)
            if not chapter_id:
                return results
            url = text.urljoin(self.root, chapter_id)
            # chapter, pos = text.extract(page,
            #     '<span class="chapternum">Chapter ', '<', pos)
            data = {
                "manga_id": self.gid,
                "chapter_id": chapter_id,
                "title": title,
            }
            chapter_match = re.search(r"\d+$", chapter_id)
            if chapter_match:
                data["chapter"] = chapter_match.group(0)
            results.append((url, data))
