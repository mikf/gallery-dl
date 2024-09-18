# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://archiveofourown.org/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?"
                r"a(?:rchiveofourown|o3)\.(?:org|com|net)")


class Ao3Extractor(Extractor):
    """Base class for ao3 extractors"""
    category = "ao3"
    root = "https://archiveofourown.org"
    categorytransfer = True
    request_interval = (0.5, 1.5)

    def items(self):
        base = self.root + "/works/"
        data = {"_extractor": Ao3WorkExtractor}

        for work_id in self.works():
            yield Message.Queue, base + work_id, data

    def works(self):
        return self._pagination(self.groups[0])

    def _pagination(self, path, needle='<li id="work_'):
        while True:
            page = self.request(self.root + path).text
            yield from text.extract_iter(page, needle, '"')
            path = text.extr(page, '<a rel="next" href="', '"')
            if not path:
                return
            path = text.unescape(path)


class Ao3WorkExtractor(Ao3Extractor):
    """Extractor for an AO3 work"""
    subcategory = "work"
    directory_fmt = ("{category}", "{author}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}.{extension}"
    pattern = BASE_PATTERN + r"/works/(\d+)"
    example = "https://archiveofourown.org/works/12345"

    def _init(self):
        formats = self.config("formats")
        if formats is None:
            self.formats = ("pdf",)
        elif not formats:
            self.formats = ()
        elif isinstance(formats, str):
            self.formats = formats.lower().replace(" ", "").split(",")
        else:
            self.formats = formats

        self.cookies.set("view_adult", "true", domain="archiveofourown.org")

    def items(self):
        work_id = self.groups[0]
        url = "{}/works/{}".format(self.root, work_id)
        extr = text.extract_from(self.request(url).text)

        chapters = {}
        cindex = extr(' id="chapter_index"', "</ul>")
        for ch in text.extract_iter(cindex, ' value="', "</option>"):
            cid, _, cname = ch.partition('">')
            chapters[cid] = text.unescape(cname)

        fmts = {}
        path = ""
        download = extr(' class="download"', "</ul>")
        for dl in text.extract_iter(download, ' href="', "</"):
            path, _, type = dl.rpartition('">')
            fmts[type.lower()] = path

        data = {
            "id"           : text.parse_int(work_id),
            "rating"       : text.split_html(
                extr('<dd class="rating tags">', "</dd>")),
            "warnings"     : text.split_html(
                extr('<dd class="warning tags">', "</dd>")),
            "categories"   : text.split_html(
                extr('<dd class="category tags">', "</dd>")),
            "fandom"       : text.split_html(
                extr('<dd class="fandom tags">', "</dd>")),
            "relationships": text.split_html(
                extr('<dd class="relationship tags">', "</dd>")),
            "characters"   : text.split_html(
                extr('<dd class="character tags">', "</dd>")),
            "tags"         : text.split_html(
                extr('<dd class="freeform tags">', "</dd>")),
            "lang"         : extr('<dd class="language" lang="', '"'),
            "series"       : extr('<dd class="series">', "</dd>"),
            "date"         : text.parse_datetime(
                extr('<dd class="published">', "<"), "%Y-%m-%d"),
            "date_completed": text.parse_datetime(
                extr('>Completed:</dt><dd class="status">', "<"), "%Y-%m-%d"),
            "date_updated" : text.parse_timestamp(
                path.rpartition("updated_at=")[2]),
            "words"        : text.parse_int(
                extr('<dd class="words">', "<").replace(",", "")),
            "chapters"     : chapters,
            "comments"     : text.parse_int(
                extr('<dd class="comments">', "<").replace(",", "")),
            "likes"        : text.parse_int(
                extr('<dd class="kudos">', "<").replace(",", "")),
            "bookmarks"    : text.parse_int(text.remove_html(
                extr('<dd class="bookmarks">', "</dd>")).replace(",", "")),
            "views"        : text.parse_int(
                extr('<dd class="hits">', "<").replace(",", "")),
            "title"        : text.unescape(
                extr(' class="title heading">', "<").strip()),
            "author"       : text.unescape(text.remove_html(
                extr(' class="byline heading">', "</h3>"))),
            "summary"      : text.split_html(
                extr(' class="heading">Summary:</h3>', "</div>")),
        }
        data["language"] = util.code_to_language(data["lang"])

        series = data["series"]
        if series:
            extr = text.extract_from(series)
            data["series"] = {
                "prev" : extr(' class="previous" href="/works/', '"'),
                "index": extr(' class="position">Part ', " "),
                "id"   : extr(' href="/series/', '"'),
                "name" : text.unescape(extr(">", "<")),
                "next" : extr(' class="next" href="/works/', '"'),
            }
        else:
            data["series"] = None

        yield Message.Directory, data
        for fmt in self.formats:
            try:
                url = text.urljoin(self.root, fmts[fmt])
            except KeyError:
                self.log.warning("%s: Format '%s' not available", work_id, fmt)
            else:
                yield Message.Url, url, text.nameext_from_url(url, data)


class Ao3SeriesExtractor(Ao3Extractor):
    """Extractor for AO3 works of a series"""
    subcategory = "series"
    pattern = BASE_PATTERN + r"(/series/(\d+))"
    example = "https://archiveofourown.org/series/12345"


class Ao3TagExtractor(Ao3Extractor):
    """Extractor for AO3 works by tag"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"(/tags/([^/?#]+)/works(?:/?\?.+)?)"
    example = "https://archiveofourown.org/tags/TAG/works"


class Ao3SearchExtractor(Ao3Extractor):
    """Extractor for AO3 search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"(/works/search/?\?.+)"
    example = "https://archiveofourown.org/works/search?work_search[query]=air"


class Ao3UserExtractor(Ao3Extractor):
    """Extractor for an AO3 user profile"""
    subcategory = "user"
    pattern = (BASE_PATTERN + r"/users/([^/?#]+(?:/pseuds/[^/?#]+)?)"
               r"(?:/profile)?/?(?:$|\?|#)")
    example = "https://archiveofourown.org/users/USER"

    def initialize(self):
        pass

    def items(self):
        base = "{}/users/{}/".format(self.root, self.groups[0])
        return self._dispatch_extractors((
            (Ao3UserWorksExtractor   , base + "works"),
            (Ao3UserSeriesExtractor  , base + "series"),
            (Ao3UserBookmarkExtractor, base + "bookmarks"),
        ), ("user-works", "user-series"))


class Ao3UserWorksExtractor(Ao3Extractor):
    """Extractor for works of an AO3 user"""
    subcategory = "user-works"
    pattern = (BASE_PATTERN + r"(/users/([^/?#]+)/(?:pseuds/([^/?#]+)/)?"
               r"works(?:/?\?.+)?)")
    example = "https://archiveofourown.org/users/USER/works"


class Ao3UserSeriesExtractor(Ao3Extractor):
    """Extractor for series of an AO3 user"""
    subcategory = "user-series"
    pattern = (BASE_PATTERN + r"(/users/([^/?#]+)/(?:pseuds/([^/?#]+)/)?"
               r"series(?:/?\?.+)?)")
    example = "https://archiveofourown.org/users/USER/series"

    def items(self):
        base = self.root + "/series/"
        data = {"_extractor": Ao3SeriesExtractor}

        for series_id in self.series():
            yield Message.Queue, base + series_id, data

    def series(self):
        return self._pagination(self.groups[0], '<li id="series_')


class Ao3UserBookmarkExtractor(Ao3Extractor):
    """Extractor for bookmarked works of an AO3 user"""
    subcategory = "user-bookmark"
    pattern = (BASE_PATTERN + r"(/users/([^/?#]+)/(?:pseuds/([^/?#]+)/)?"
               r"bookmarks(?:/?\?.+)?)")
    example = "https://archiveofourown.org/users/USER/bookmarks"
