# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://acgxmh.com/"""

from .common import GalleryExtractor
from .. import text


class AcgxmhChapterExtractor(GalleryExtractor):
    """Extractor for manga chapters from acgxmh.com"""
    category = "acgxmh"
    root = "https://acgxmh.com"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{title}_{num:>03}.{extension}"
    archive_fmt = "{chapter_id}_{num}"
    pattern = r"(?:https?://)?acgxmh\.com/h/(\d+)(?:-\d+)?\.html"
    example = "https://acgxmh.com/h/12345.html"

    def __init__(self, match):
        self.chapter_id = match.group(1)
        url = f"{self.root}/h/{self.chapter_id}.html"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = text.extr(page, '<h1 class="title">', '</h1>')
        # Remove trailing page indicator like "(2)" from sub-pages
        if title.endswith(")"):
            paren = title.rfind("(")
            if paren != -1 and title[paren+1:-1].isdigit():
                title = title[:paren].strip()

        lang_text = text.extr(page, 'class="lang_cat"', '</a>')
        lang_text = lang_text.rpartition(">")[2]

        date = text.extr(page, "<span>时间:", "</span>").strip()

        summary = text.extr(page, '<div class="summary">', '</div>')

        parody_block = text.extr(summary, "戏仿：", "</span>")
        parody = list(text.extract_iter(parody_block, '">', '</a>'))

        artist_block = text.extr(summary, "作者：", "</span>")
        artist = list(text.extract_iter(artist_block, '">', '</a>'))

        tags_block = text.extr(summary, "标签：", "</span>")
        tags = list(text.extract_iter(tags_block, '">', '</a>'))

        # Determine total page count from the pagination div
        # href values look like "785691" (page 1) or "785691-6" (page 6)
        pages_nav = text.extr(page, 'id="pages">', '</div>')
        page_nums = []
        for m in text.extract_iter(pages_nav, 'href="/h/', '.html"'):
            if "-" in m:
                suffix = m.rsplit("-", 1)[-1]
                if suffix.isdigit():
                    page_nums.append(int(suffix))
        count = max(page_nums) if page_nums else 1

        return {
            "title"     : text.unescape(title),
            "chapter_id": text.parse_int(self.chapter_id),
            "lang"      : self._lang_code(lang_text),
            "language"  : lang_text,
            "date"      : date,
            "parody"    : parody,
            "artist"    : artist,
            "tags"      : tags,
            "count"     : count,
        }

    def images(self, page):
        # Extract image from the first page
        results = [self._extract_image(page)]

        # Determine total page count from the pagination div
        pages_nav = text.extr(page, 'id="pages">', '</div>')
        page_nums = []
        for m in text.extract_iter(pages_nav, 'href="/h/', '.html"'):
            if "-" in m:
                suffix = m.rsplit("-", 1)[-1]
                if suffix.isdigit():
                    page_nums.append(int(suffix))
        count = max(page_nums) if page_nums else 1

        # Fetch remaining pages
        for page_num in range(2, count + 1):
            url = f"{self.root}/h/{self.chapter_id}-{page_num}.html"
            subpage = self.request(url).text
            results.append(self._extract_image(subpage))

        return results

    def _extract_image(self, page):
        block = text.extr(page, '<p class="manga-picture">', '</p>')
        url = text.extr(block, 'src="', '"')
        width = text.parse_int(text.extr(block, 'width="', '"'))
        height = text.parse_int(text.extr(block, 'height="', '"'))
        imgdata = {}
        if width:
            imgdata["width"] = width
        if height:
            imgdata["height"] = height
        return (url, imgdata or None)

    @staticmethod
    def _lang_code(lang_text):
        mapping = {
            "英文译本": "en",
            "中文": "zh",
            "日本語": "ja",
            "汉化中文": "zh",
            "Español": "es",
            "Korean": "ko",
        }
        for key, code in mapping.items():
            if key in lang_text:
                return code
        return ""
