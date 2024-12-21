# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tapas.io/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?tapas\.io"


class TapasExtractor(Extractor):
    """Base class for tapas.io extractors"""
    category = "tapas"
    root = "https://tapas.io"
    directory_fmt = ("{category}", "{series[title]}", "{id} {title}")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    cookies_domain = ".tapas.io"
    cookies_names = ("_cpc_",)
    _cache = None

    def _init(self):
        if self._cache is None:
            TapasExtractor._cache = {}

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

        self.cookies.set(
            "birthDate"        , "1981-02-03", domain=self.cookies_domain)
        self.cookies.set(
            "adjustedBirthDate", "1981-02-03", domain=self.cookies_domain)

    @cache(maxage=14*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/account/authenticate"
        headers = {
            "Referer" : url,
        }
        data = {
            "from"    : "https://tapas.io/",
            "email"   : username,
            "password": password,
        }
        response = self.request(
            url, method="POST", headers=headers, data=data)

        if not response.history or \
                "/account/signin_fail" in response.history[-1].url:
            raise exception.AuthenticationError()

        return {"_cpc_": response.history[0].cookies.get("_cpc_")}

    def request_api(self, url, params=None):
        headers = {"Accept": "application/json, text/javascript, */*;"}
        return self.request(url, params=params, headers=headers).json()["data"]


class TapasEpisodeExtractor(TapasExtractor):
    subcategory = "episode"
    pattern = BASE_PATTERN + r"/episode/(\d+)"
    example = "https://tapas.io/episode/12345"

    def items(self):
        self.login()

        episode_id = self.groups[0]
        url = "{}/episode/{}".format(self.root, episode_id)
        data = self.request_api(url)

        episode = data["episode"]
        if not episode.get("free") and not episode.get("unlocked"):
            raise exception.AuthorizationError(
                "{}: Episode '{}' not unlocked".format(
                    episode_id, episode["title"]))

        html = data["html"]
        episode["series"] = self._extract_series(html)
        episode["date"] = text.parse_datetime(episode["publish_date"])
        yield Message.Directory, episode

        if episode["book"]:
            content = text.extr(
                html, '<div class="viewer">', '<div class="viewer-bottom')
            episode["num"] = 1
            episode["extension"] = "html"
            yield Message.Url, "text:" + content, episode

        else:  # comic
            for episode["num"], url in enumerate(text.extract_iter(
                    html, 'data-src="', '"'), 1):
                yield Message.Url, url, text.nameext_from_url(url, episode)

    def _extract_series(self, html):
        series_id = text.rextract(html, 'data-series-id="', '"')[0]
        try:
            return self._cache[series_id]
        except KeyError:
            url = "{}/series/{}".format(self.root, series_id)
            series = self._cache[series_id] = self.request_api(url)
            return series


class TapasSeriesExtractor(TapasExtractor):
    subcategory = "series"
    pattern = BASE_PATTERN + r"/series/([^/?#]+)"
    example = "https://tapas.io/series/TITLE"

    def items(self):
        self.login()

        url = "{}/series/{}".format(self.root, self.groups[0])
        series_id, _, episode_id = text.extr(
            self.request(url).text, 'content="tapastic://series/', '"',
        ).partition("/episodes/")

        url = "{}/series/{}/episodes".format(self.root, series_id)
        params = {
            "eid"        : episode_id,
            "page"       : 1,
            "sort"       : "OLDEST",
            "last_access": "0",
            "max_limit"  : "20",
        }

        base = self.root + "/episode/"
        while True:
            data = self.request_api(url, params)
            for episode in data["episodes"]:
                episode["_extractor"] = TapasEpisodeExtractor
                yield Message.Queue, base + str(episode["id"]), episode

            if not data["pagination"]["has_next"]:
                return
            params["page"] += 1


class TapasCreatorExtractor(TapasExtractor):
    subcategory = "creator"
    pattern = BASE_PATTERN + r"/(?!series|episode)([^/?#]+)"
    example = "https://tapas.io/CREATOR"

    def items(self):
        self.login()

        url = "{}/{}/series".format(self.root, self.groups[0])
        page = self.request(url).text
        page = text.extr(page, '<ul class="content-list-wrap', "</ul>")

        data = {"_extractor": TapasSeriesExtractor}
        for path in text.extract_iter(page, ' href="', '"'):
            yield Message.Queue, self.root + path, data
