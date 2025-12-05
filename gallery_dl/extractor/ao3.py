# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://archiveofourown.org/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?"
                r"a(?:rchiveofourown|o3)\.(?:org|com|net)")


class Ao3Extractor(Extractor):
    """Base class for ao3 extractors"""
    category = "ao3"
    root = "https://archiveofourown.org"
    categorytransfer = True
    cookies_domain = ".archiveofourown.org"
    cookies_names = ("remember_user_token",)
    request_interval = (0.5, 1.5)

    def items(self):
        self.login()

        base = self.root + "/works/"
        data = {"_extractor": Ao3WorkExtractor, "type": "work"}

        for work_id in self.works():
            yield Message.Queue, base + work_id, data

    def items_list(self, type, needle, part=True):
        self.login()

        base = self.root + "/"
        data_work = {"_extractor": Ao3WorkExtractor, "type": "work"}
        data_series = {"_extractor": Ao3SeriesExtractor, "type": "series"}
        data_user = {"_extractor": Ao3UserExtractor, "type": "user"}

        for item in self._pagination(self.groups[0], needle):
            path = item.rpartition("/")[0] if part else item
            url = base + path
            if item.startswith("works/"):
                yield Message.Queue, url, data_work
            elif item.startswith("series/"):
                yield Message.Queue, url, data_series
            elif item.startswith("users/"):
                yield Message.Queue, url, data_user
            else:
                self.log.warning("Unsupported %s type '%s'", type, path)

    def works(self):
        return self._pagination(self.groups[0])

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/users/login"
        page = self.request(url).text

        pos = page.find('id="loginform"')
        token = text.extract(
            page, ' name="authenticity_token" value="', '"', pos)[0]
        if not token:
            self.log.error("Unable to extract 'authenticity_token'")

        data = {
            "authenticity_token": text.unescape(token),
            "user[login]"       : username,
            "user[password]"    : password,
            "user[remember_me]" : "1",
            "commit"            : "Log In",
        }

        response = self.request(url, method="POST", data=data)
        if not response.history:
            raise exception.AuthenticationError()

        remember = response.history[0].cookies.get("remember_user_token")
        if not remember:
            raise exception.AuthenticationError()

        return {
            "remember_user_token": remember,
            "user_credentials"   : "1",
        }

    def _pagination(self, path, needle='<li id="work_'):
        while True:
            page = self.request(self.root + path).text

            yield from text.extract_iter(page, needle, '"')

            path = (text.extr(page, '<a rel="next" href="', '"') or
                    text.extr(page, '<li class="next"><a href="', '"'))
            if not path:
                return
            path = text.unescape(path)


class Ao3WorkExtractor(Ao3Extractor):
    """Extractor for an AO3 work"""
    subcategory = "work"
    directory_fmt = ("{category}", "{author}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}.{extension}"
    pattern = rf"{BASE_PATTERN}/works/(\d+)"
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
        self.login()

        work_id = self.groups[0]
        url = f"{self.root}/works/{work_id}"
        response = self.request(url, notfound="work")

        if response.url.endswith("/users/login?restricted=true"):
            raise exception.AuthorizationError(
                "Login required to access member-only works")
        page = response.text
        if len(page) < 20000 and \
                '<h2 class="landmark heading">Adult Content Warning</' in page:
            raise exception.AbortExtraction("Adult Content")

        extr = text.extract_from(page)

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
            "date"         : self.parse_datetime_iso(extr(
                '<dd class="published">', "<")),
            "date_completed": self.parse_datetime_iso(extr(
                '>Completed:</dt><dd class="status">', "<")),
            "date_updated" : self.parse_timestamp(
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
            "title"        : text.unescape(text.remove_html(
                extr(' class="title heading">', "</h2>")).strip()),
            "author"       : text.unescape(text.remove_html(
                extr(' class="byline heading">', "</h3>"))),
            "summary"      : text.split_html(
                extr(' class="heading">Summary:</h3>', "</div>")),
        }
        data["language"] = util.code_to_language(data["lang"])

        if series := data["series"]:
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

        yield Message.Directory, "", data
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
    pattern = rf"{BASE_PATTERN}(/series/(\d+))"
    example = "https://archiveofourown.org/series/12345"


class Ao3TagExtractor(Ao3Extractor):
    """Extractor for AO3 works by tag"""
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}(/tags/([^/?#]+)/works(?:/?\?.+)?)"
    example = "https://archiveofourown.org/tags/TAG/works"


class Ao3SearchExtractor(Ao3Extractor):
    """Extractor for AO3 search results"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}(/works/search/?\?.+)"
    example = "https://archiveofourown.org/works/search?work_search[query]=air"


class Ao3UserExtractor(Dispatch, Ao3Extractor):
    """Extractor for an AO3 user profile"""
    pattern = (rf"{BASE_PATTERN}/users/([^/?#]+(?:/pseuds/[^/?#]+)?)"
               rf"(?:/profile)?/?(?:$|\?|#)")
    example = "https://archiveofourown.org/users/USER"

    def items(self):
        base = f"{self.root}/users/{self.groups[0]}/"
        return self._dispatch_extractors((
            (Ao3UserWorksExtractor   , base + "works"),
            (Ao3UserSeriesExtractor  , base + "series"),
            (Ao3UserBookmarkExtractor, base + "bookmarks"),
        ), ("user-works", "user-series"))


class Ao3UserWorksExtractor(Ao3Extractor):
    """Extractor for works of an AO3 user"""
    subcategory = "user-works"
    pattern = (rf"{BASE_PATTERN}(/users/([^/?#]+)/(?:pseuds/([^/?#]+)/)?"
               rf"works(?:/?\?.+)?)")
    example = "https://archiveofourown.org/users/USER/works"


class Ao3UserSeriesExtractor(Ao3Extractor):
    """Extractor for series of an AO3 user"""
    subcategory = "user-series"
    pattern = (rf"{BASE_PATTERN}(/users/([^/?#]+)/(?:pseuds/([^/?#]+)/)?"
               rf"series(?:/?\?.+)?)")
    example = "https://archiveofourown.org/users/USER/series"

    def items(self):
        self.login()

        base = self.root + "/series/"
        data = {"_extractor": Ao3SeriesExtractor}

        for series_id in self.series():
            yield Message.Queue, base + series_id, data

    def series(self):
        return self._pagination(self.groups[0], '<li id="series_')


class Ao3UserBookmarkExtractor(Ao3Extractor):
    """Extractor for bookmarked works of an AO3 user"""
    subcategory = "user-bookmark"
    pattern = (rf"{BASE_PATTERN}(/users/([^/?#]+)/(?:pseuds/([^/?#]+)/)?"
               rf"bookmarks(?:/?\?.+)?)")
    example = "https://archiveofourown.org/users/USER/bookmarks"

    def items(self):
        return self.items_list("bookmark", '<span class="count"><a href="/')


class Ao3SubscriptionsExtractor(Ao3Extractor):
    """Extractor for your AO3 account's subscriptions"""
    subcategory = "subscriptions"
    pattern = rf"{BASE_PATTERN}(/users/([^/?#]+)/subscriptions(?:/?\?.+)?)"
    example = "https://archiveofourown.org/users/USER/subscriptions"

    def items(self):
        return self.items_list("subscription", '<dt>\n<a href="/', False)
