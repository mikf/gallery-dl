# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://doujindesu.tv/"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, util
import urllib.parse

BASE_PATTERN = r"(?:https?://)?(?:www\.)?doujindesu\.tv"


class DoujindesuExtractor(Extractor):
    """Base extractor for doujindesu."""
    category = "doujindesu"
    root = "https://doujindesu.tv"

    directory_fmt = ("{category}", "{manga}", "{_subfolder}")
    filename_fmt = "{manga}{_chapter_suffix}_{_num:>03}.{extension}"
    archive_fmt = "{manga}{_chapter_suffix}_{_num}"

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }

    EXCLUDED_PATHS = {
        "/register/", "/login/",
        "/logout.php", "/myaccount/",
        "/privacy-policy/", "/terms/",
    }

    @staticmethod
    def clean_title(title):
        """Remove site suffixes and normalize title."""
        return title.replace(" - Doujindesu", "").replace(".XXX", "").strip()

    @staticmethod
    def safe_url(url):
        """Encode only path and query of an URL (preserve scheme/netloc)."""
        parts = urllib.parse.urlsplit(url)
        safe_path = urllib.parse.quote(parts.path, safe="/%()")
        safe_query = urllib.parse.quote(parts.query, safe="=&")
        return urllib.parse.urlunsplit(
            (parts.scheme, parts.netloc, safe_path, safe_query, parts.fragment)
        )

    def parse_chapter_string(self, chapter_string, data=None):
        """
        Parse a title string and fill manga/chapter metadata.

        Sets:
        - manga (str)
        - chapter (int) only for chapter items
        - _has_chapter (bool)
        - _subfolder (str) like 'c001' or ''
        - _chapter_suffix (str) like '_c001' or ''
        - title, lang, language
        """
        if data is None:
            data = {}

        chapter_string = text.unescape(chapter_string).strip()
        chapter_string = self.clean_title(chapter_string)

        pattern_chapter = util.re(
            r"^(.*?) Chapter (\d+)(?:\s*-\s*(.*))?$"
        )
        match = pattern_chapter.match(chapter_string)

        if match:
            data["manga"] = match.group(1).strip()
            data["chapter"] = text.parse_int(match.group(2))
            data["_has_chapter"] = True
            data["_subfolder"] = f"c{data['chapter']:03d}"
            data["_chapter_suffix"] = f"_c{data['chapter']:03d}"
            data["title"] = match.group(3) or ""
        else:
            data["manga"] = chapter_string
            data["_has_chapter"] = False
            data["_subfolder"] = ""
            data["_chapter_suffix"] = ""
            data["title"] = ""

        data["lang"] = "id"
        data["language"] = "Indonesian"
        return data


class DoujindesuChapterExtractor(DoujindesuExtractor, ChapterExtractor):
    """Extractor for chapter (and single-post) pages."""
    pattern = BASE_PATTERN + (
        r"(/(?:\d{4}/\d{2}/\d{2}/)?"
        r"(?!manga/)[^/?#]+(?:-chapter-\d+|-\d+)?/?)"
    )
    example = "https://doujindesu.tv/ini-judul-nya-chapter-23/"

    def metadata(self, page):
        """Return metadata for the page;
        ensure chapter keys only when valid."""
        title = text.extr(page, "<title>", "</title>")
        data = self.parse_chapter_string(title)

        """If URL contains explicit '-chapter-N', prefer that number."""
        url_lower = (self.url or "").lower()
        if "-chapter-" in url_lower:
            chapter_str = self.url.rstrip("/").rsplit("-chapter-", 1)[-1]
            if chapter_str.isdigit():
                data["chapter"] = int(chapter_str)
                data["_has_chapter"] = True
                data["_subfolder"] = f"c{data['chapter']:03d}"
                data["_chapter_suffix"] = f"_c{data['chapter']:03d}"

        """Clean up: remove 'chapter' key when not a chapter."""
        if not data.get("_has_chapter"):
            data.pop("chapter", None)
            data["_subfolder"] = ""
            data["_chapter_suffix"] = ""

        return data

    def images(self, page):
        """Fetch images from ch.php and return (url, metadata) tuples."""
        chapter_id = text.extr(page, 'data-id="', '"')
        if not chapter_id:
            return []

        headers = self.DEFAULT_HEADERS.copy()
        headers["Referer"] = self.url

        response = self.request(
            f"{self.root}/themes/ajax/ch.php",
            method="POST",
            headers=headers,
            data={"id": chapter_id},
        )

        img_pattern = util.re(r'<img[^>]+src=(["\'])(.*?)\1')
        info = self.metadata(page)
        manga = info.get("manga", "Unknown")
        manga = self.clean_title(manga)

        images = []
        for i, match in enumerate(img_pattern.findall(response.text), 1):
            src = match[1]
            if "desu.photos" not in src:
                continue

            """Normalize relative / protocol-relative URLs"""
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = self.root.rstrip("/") + src

            url = self.safe_url(src)
            ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
            ext = (
                ext if ext in (
                    "jpg", "jpeg", "png", "webp", "gif"
                ) else "webp"
            )

            """Provide metadata keys used by format strings"""
            item_meta = {
                "_num": i,
                "manga": manga,
                "_chapter_suffix": info.get("_chapter_suffix", ""),
                "_subfolder": info.get("_subfolder", ""),
                "extension": ext,
            }

            images.append((url, item_meta))

        return images


class DoujindesuMangaExtractor(DoujindesuExtractor, MangaExtractor):
    """Extractor for manga listing pages (chapter lists)."""
    chapterclass = DoujindesuChapterExtractor
    pattern = BASE_PATTERN + r"(/manga/[^/?#]+/?)$"
    example = "https://doujindesu.tv/manga/ini-judul-nya/"

    def chapters(self, page):
        """Return (url, metadata) pairs for
        each chapter link on a manga page."""
        results = []
        base_data = self.metadata(page)

        for item in text.extract_iter(page, "<li>", "</li>"):
            url = text.extr(item, 'href="', '"')
            title = text.extr(item, 'title="', '"') or url

            if not url or any(p in url.lower() for p in self.EXCLUDED_PATHS):
                continue

            full_url = text.urljoin(self.root, url)
            results.append((
                full_url,
                self.parse_chapter_string(title, base_data.copy())
            ))

        return results

    def metadata(self, page):
        """Return basic manga metadata (title, language) for manga pages."""
        title = text.extr(page, "<title>", "</title>")
        manga = self.clean_title(title.partition("|")[0])
        return {
            "manga": text.unescape(manga),
            "lang": "id",
            "language": "Indonesian",
            "_subfolder": "",
            "_chapter_suffix": "",
        }
