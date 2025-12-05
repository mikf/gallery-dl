# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://dynasty-scans.com/"""

from .common import ChapterExtractor, MangaExtractor, Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?dynasty-scans\.com"


class DynastyscansBase():
    """Base class for dynastyscans extractors"""
    category = "dynastyscans"
    root = "https://dynasty-scans.com"

    def _parse_image_page(self, image_id):
        url = f"{self.root}/images/{image_id}"
        extr = text.extract_from(self.request(url).text)

        date = extr("class='create_at'>", "</span>")
        tags = extr("class='tags'>", "</span>")
        src = extr("class='btn-group'>", "</div>")
        url = extr(' src="', '"')

        src = text.extr(src, 'href="', '"') if "Source<" in src else ""

        return {
            "url"     : self.root + url,
            "image_id": text.parse_int(image_id),
            "tags"    : text.split_html(tags),
            "date"    : text.remove_html(date),
            "source"  : text.unescape(src),
        }


class DynastyscansChapterExtractor(DynastyscansBase, ChapterExtractor):
    """Extractor for manga-chapters from dynasty-scans.com"""
    pattern = rf"{BASE_PATTERN}(/chapters/[^/?#]+)"
    example = "https://dynasty-scans.com/chapters/NAME"

    def metadata(self, page):
        extr = text.extract_from(page)
        match = text.re(
            r"(?:<a[^>]*>)?([^<]+)(?:</a>)?"  # manga name
            r"(?: ch(\d+)([^:<]*))?"  # chapter info
            r"(?:: (.+))?"  # title
        ).match(extr("<h3 id='chapter-title'><b>", "</b>"))
        author = extr(" by ", "</a>")
        group = extr('"icon-print"></i> ', '</span>')

        return {
            "manga"   : text.unescape(match[1]),
            "chapter" : text.parse_int(match[2]),
            "chapter_minor": match[3] or "",
            "title"   : text.unescape(match[4] or ""),
            "author"  : text.remove_html(author),
            "group"   : (text.remove_html(group) or
                         text.extr(group, ' alt="', '"')),
            "date"    : self.parse_datetime(extr(
                '"icon-calendar"></i> ', '<'), "%b %d, %Y"),
            "tags"    : text.split_html(extr(
                "class='tags'>", "<div id='chapter-actions'")),
            "lang"    : "en",
            "language": "English",
        }

    def images(self, page):
        data = text.extr(page, "var pages = ", ";\n")
        return [
            (self.root + img["image"], None)
            for img in util.json_loads(data)
        ]


class DynastyscansMangaExtractor(DynastyscansBase, MangaExtractor):
    chapterclass = DynastyscansChapterExtractor
    reverse = False
    pattern = rf"{BASE_PATTERN}(/series/[^/?#]+)"
    example = "https://dynasty-scans.com/series/NAME"

    def chapters(self, page):
        return [
            (self.root + path, {})
            for path in text.extract_iter(page, '<dd>\n<a href="', '"')
        ]


class DynastyscansSearchExtractor(DynastyscansBase, Extractor):
    """Extrator for image search results on dynasty-scans.com"""
    subcategory = "search"
    directory_fmt = ("{category}", "Images")
    filename_fmt = "{image_id}.{extension}"
    archive_fmt = "i_{image_id}"
    pattern = rf"{BASE_PATTERN}/images/?(?:\?([^#]+))?$"
    example = "https://dynasty-scans.com/images?QUERY"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match[1] or ""

    def items(self):
        yield Message.Directory, "", {}
        for image_id in self.images():
            image = self._parse_image_page(image_id)
            url = image["url"]
            yield Message.Url, url, text.nameext_from_url(url, image)

    def images(self):
        url = self.root + "/images?" + self.query.replace("[]", "%5B%5D")
        params = {"page": 1}

        while True:
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, '"/images/', '"')
            if 'rel="next"' not in page:
                return
            params["page"] += 1


class DynastyscansImageExtractor(DynastyscansSearchExtractor):
    """Extractor for individual images on dynasty-scans.com"""
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/images/(\d+)"
    example = "https://dynasty-scans.com/images/12345"

    def images(self):
        return (self.query,)


class DynastyscansAnthologyExtractor(DynastyscansSearchExtractor):
    """Extractor for dynasty-scans anthologies"""
    subcategory = "anthology"
    pattern = rf"{BASE_PATTERN}/anthologies/([^/?#]+)"
    example = "https://dynasty-scans.com/anthologies/TITLE"

    def items(self):
        url = f"{self.root}/anthologies/{self.groups[0]}.atom"
        root = self.request_xml(url, xmlns=False)

        data = {
            "_extractor": DynastyscansChapterExtractor,
            "anthology" : root[3].text[28:],
        }

        if self.config("metadata", False):
            page = self.request(url[:-5]).text
            alert = text.extr(page, "<div class='alert", "</div>")

            data["alert"] = text.split_html(alert)[1:] if alert else ()
            data["status"] = text.extr(
                page, "<small>&mdash; ", "</small>")
            data["description"] = text.extr(
                page, "<div class='description'>", "</div>")

        for element in root:
            if element.tag != "entry":
                continue
            content = element[6][0]
            data["author"] = content[0].text[8:]
            data["scanlator"] = content[1].text[11:]
            data["tags"] = content[2].text[6:].lower().split(", ")
            data["title"] = element[5].text
            data["date"] = self.parse_datetime_iso(element[1].text)
            data["date_updated"] = self.parse_datetime_iso(element[2].text)
            yield Message.Queue, element[4].text, data
