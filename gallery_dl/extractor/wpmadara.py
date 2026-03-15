# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for WordPressMadara based websites."""

from .common import ChapterExtractor, Extractor, MangaExtractor, Message
from .. import text


class WPMadaraBase():
    """Base class for WordPressMadara extractors"""
    basecategory = "wpmadara"

    def manga_data(self, manga_slug, page=None):
        if page is None:
            url = "{}/{}/".format(self.root.rstrip("/"), manga_slug.strip("/"))
            page = self.request(url).text

        # Build label->value map from post-content_item blocks
        info = {}
        for item in page.split('class="post-content_item">')[1:]:
            label = text.remove_html(text.extr(item, "<h5>", "</h5>")).strip()
            value = text.extr(item, 'class="summary-content">', "</div>")
            if label:
                info[label] = value

        authors = list(text.extract_iter(
            info.get("Writer(s)", info.get("Author(s)", "")),
            '"tag">', "</a>"))
        artists = list(text.extract_iter(
            info.get("Artist(s)", ""), '"tag">', "</a>"))
        genres = list(text.extract_iter(
            info.get("Genre(s)", ""), '"tag">', "</a>"))
        alt = text.remove_html(
            info.get("Alt Name(s)", info.get("Alternative", ""))
        ).strip()

        return {
            "manga"      : text.extr(page, "<h1>", "</h1>").strip(),
            "description": text.unescape(text.remove_html(text.extract(
                page, ">", "</div>",
                page.index("summary__content"))[0])),
            "rating"     : text.parse_float(
                text.extr(page, 'class="score font-meta total_votes">',
                          "</span>").strip()),
            "manga_alt"  : alt.split("; ") if alt else [],
            "author"     : authors,
            "artist"     : artists,
            "genres"     : genres,
            "type"       : text.remove_html(
                info.get("Type", "")).strip(),
            "release"    : text.parse_int(text.remove_html(
                info.get("Release", ""))),
            "status"     : text.remove_html(
                info.get("Status", "")).strip(),
        }

    def parse_chapter_string(self, chapter_string, data):
        match = text.re(
            r"(?:(.+?)\s*-?\s*)?[Cc]hapter\s*(\d+)(\.\d+)?(?:\s*[:-]?\s*(.+))?"
        ).match(text.unescape(chapter_string).strip())
        if match:
            manga, chapter, minor, title = match.groups()
        else:
            manga, chapter, minor, title = "", "0", "", chapter_string
        manga = manga.strip() if manga else ""
        data["manga"] = data.pop("manga", manga)
        data["chapter"] = text.parse_int(chapter)
        data["chapter_minor"] = minor or ""
        data["title"] = title or ""
        data["lang"] = "en"
        data["language"] = "English"


class WPMadaraHomeExtractor(WPMadaraBase, Extractor):
    """Base home extractor for WordPressMadara based websites"""
    subcategory = "home"
    mangaextractor = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page = text.parse_int(match[1], 1)

    def items(self):
        data = {"_extractor": self.mangaextractor}
        url = self.page_url(self.page)

        while True:
            page = self.request(url).text
            for manga in self.mangas(page):
                yield Message.Queue, manga, data

            url = self.next_page(url, page)
            if url is None:
                return

    def page_url(self, page_num):
        if page_num == 1:
            return self.root + "/"
        return "{}/page/{}/".format(self.root.rstrip("/"), page_num)

    def next_page(self, url, page):
        for anchor in text.extract_iter(page, "<a ", "</a>"):
            if "nextpostslink" not in anchor:
                continue
            next_url = text.unescape(text.extr(anchor, 'href="', '"').strip())
            if next_url:
                return text.urljoin(url, next_url)
        return None

    def mangas(self, page):
        seen = set()

        for item in page.split('class="page-item-detail manga')[1:]:
            url = text.unescape(text.extr(item, '<a href="', '"').strip())
            if not url or url in seen:
                continue
            seen.add(url)
            yield url


class WPMadaraChapterExtractor(WPMadaraBase, ChapterExtractor):
    """Base chapter extractor for WordPressMadara based websites"""

    def metadata(self, page):
        tags = text.extr(page, 'class="wp-manga-tags-list">', '</div>')
        manga_slug = self.groups[0].rstrip("/").rpartition("/")[0]
        data = {
            **self.cache(self.manga_data, manga_slug),
            "tags": list(text.split_html(tags)[::2]) if tags else [],
        }
        info = text.extr(page, '<h1 id="chapter-heading">', "</h1>")
        if not info:
            raise self.exc.NotFoundError("chapter")
        self.parse_chapter_string(info, data)
        return data

    def images(self, page):
        page = text.extr(
            page, '<div class="reading-content">', '<div class="entry-header')
        return [
            (url, None)
            for block in text.extract_iter(
                page, '<div class="page-break', '</div>')
            for url in (
                text.extr(block, 'data-src="', '"').strip() or
                text.extr(block, 'src="', '"').strip(),
            )
            if url
        ]


class WPMadaraMangaExtractor(WPMadaraBase, MangaExtractor):
    """Base manga extractor for WordPressMadara based websites"""
    chapterclass = WPMadaraChapterExtractor

    def chapters(self, page):
        if 'class="error404' in page:
            raise self.exc.NotFoundError("manga")
        data = self.cache(self.manga_data, self.groups[0], page)

        manga_id = text.extr(page, 'id="manga-chapters-holder"', '>')
        manga_id = text.extr(manga_id, 'data-id="', '"')

        if manga_id:
            url = self.root.rstrip("/") + "/wp-admin/admin-ajax.php"
            response = self.request(
                url, method="POST",
                data={"action": "manga_get_chapters", "manga": manga_id},
            ).text
        else:
            response = page

        results = []
        for chapter in text.extract_iter(
                response, '<li class="wp-manga-chapter', "</li>"):
            url, pos = text.extract(chapter, '<a href="', '"')
            if not url:
                continue
            info, _ = text.extract(chapter, ">", "</a>", pos)
            self.parse_chapter_string(info, data)
            results.append((url, data.copy()))
        return results
