# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comicfury.com"""

import re
import itertools
from .common import Extractor, Message
from .. import text


CF_DOMAINS = (
    r"([\w-]+)\.(?:thecomicseries\.com|the-comic\.org"
    r"|thecomicstrip\.org|webcomic\.ws|cfw\.me)"
)


class ComicfuryExtractor(Extractor):
    """Base class for ComicFury extractors"""
    category = "comicfury"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{category}_{comic}_{id}_{num:>02}.{extension}"
    archive_fmt = "{filename}"
    root = "https://comicfury.com"
    cookies_domain = "comicfury.com"

    def _init(self):
        self._search_segments = re.compile(
            (r'\n *<div class="is--image-segments">\n'
             r'([\s\S]+?)\n *</div>\n')).search

    def request(self, url, **kwargs):
        resp = Extractor.request(self, url, **kwargs)
        if '<div class="nhead">Content Warning</div>' in resp.text:
            token = self.session.cookies.get(
                "token", domain=self.cookies_domain)
            resp = Extractor.request(self, url, method="POST", data={
                "proceed": "View Webcomic",
                "token": token,
            }, **kwargs)
        return resp

    def _parse_page(self, page):
        comic_name, pos = text.extract(
            page, '<h2 class="webcomic-title-content-inner">', '</h2>')
        relative_id, pos = text.extract(
            page, 'Comic #', ':', pos)
        comic, pos = text.extract(
            page, '<a href="/comicprofile.php?url=', '"', pos)

        relative_id = int(relative_id)

        while True:
            id, pos = text.extract(
                page, '<div class="is--comic-page" id="comic-', '"', pos)
            if not id:
                break
            chapter_id, pos = text.extract(
                page, ' data-chapter-id="', '"', pos)
            chapter_name, pos = text.extract(
                page, ' data-chapter-name="', '"', pos)
            pos = text.extract(
                page, '<div class="is--title" style="', '"', pos)[1]
            title, pos = text.extract(page, '>', '</div>', pos)

            segments = self._search_segments(page, pos)
            pos = segments.end(0)
            urls = list(text.extract_iter(
                segments.group(1), '<img src="', '"'))

            data = {
                "comic_name": text.unescape(comic_name),
                "comic": comic,
                "relative_id": relative_id,
                "id": int(id),
                "chapter_id": int(chapter_id),
                "chapter_name": text.unescape(chapter_name),
                "title": text.unescape(title),
                "count": len(urls)
            }
            yield Message.Directory, data
            for data["num"], url in enumerate(urls, 1):
                url = text.unescape(url)
                yield Message.Url, url, text.nameext_from_url(url, data)

            relative_id += 1


class ComicfuryIssueExtractor(ComicfuryExtractor):
    """Extractor for a single issue URL"""
    subcategory = "issue"
    pattern = (r"(?:https?://)?(?:comicfury\.com/read/([\w-]+)(?:/comics?/"
               r"(first|last|\d+)?)?|" + CF_DOMAINS + r"/comics/"
               r"(first|1|pl/\d+)?)(?:[?#].*)?$")
    example = "https://comicfury.com/read/URL/comics/1234"

    def __init__(self, match):
        ComicfuryExtractor.__init__(self, match)
        self.comic = match.group(1) or match.group(3)
        if match.group(1) is not None:
            self.id = match.group(2) or ""
        else:
            id = match.group(4)
            if id in ("first", "1"):
                self.id = "first"
            elif not id:
                self.id = "last"
            else:
                self.id = id[3:]

    def items(self):
        url = self.root + "/read/" + self.comic + "/comics/" + self.id
        page = self.request(url).text
        iter = self._parse_page(page)

        msg, data = next(iter)
        yield msg, data
        yield from itertools.islice(iter, data["count"])


class ComicfuryComicExtractor(ComicfuryExtractor):
    """Extractor for an entire comic"""
    subcategory = "comic"
    pattern = (r"(?:https?://)?(?:comicfury\.com/comicprofile\.php"
               r"\?url=([\w-]+)|" + CF_DOMAINS + r")/?(?:[?#].*)?$")
    example = "https://comicfury.com/comicprofile.php?url=URL"

    def __init__(self, match):
        ComicfuryExtractor.__init__(self, match)
        self.comic = match.group(1) or match.group(2)

    def items(self):
        url = self.root + "/read/" + self.comic + "/comics/first"
        while True:
            page = self.request(url).text
            yield from self._parse_page(page)

            div = text.extr(
                page, '<div class="final-next-page-link-container">', '</div>')
            new_url = text.extr(
                div, '<a href="', '" class="final-next-page-link">')
            if not new_url:
                break
            url = text.urljoin(url, text.unescape(new_url))
