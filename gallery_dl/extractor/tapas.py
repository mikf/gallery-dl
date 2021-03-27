# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tapas.io/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?tapas\.io"


class TapasExtractor(Extractor):
    """Extractor for manga-chapters from tapas.io"""
    category = "tapas"
    root = "https://tapas.io"
    directory_fmt = ("{category}", "{series[title]}", "{id} {title}")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    _cache = {}

    def __init__(self, match):
        Extractor.__init__(self, match)
        setcookie = self.session.cookies.set
        setcookie("birthDate"        , "1981-02-03", domain=".tapas.io")
        setcookie("adjustedBirthDate", "1981-02-03", domain=".tapas.io")

    def items(self):
        headers = {"Accept": "application/json, text/javascript, */*;"}

        for episode_id in self.episode_ids():
            url = "{}/episode/{}".format(self.root, episode_id)
            data = self.request(url, headers=headers).json()["data"]

            episode = data["episode"]
            if not episode.get("free") and not episode.get("unlocked"):
                raise exception.StopExtraction(
                    "Episode '%s' not unlocked (ID %s) ",
                    episode["title"], episode_id)

            html = data["html"]
            series_id = text.rextract(html, 'data-series-id="', '"')[0]
            try:
                episode["series"] = self._cache[series_id]
            except KeyError:
                url = "{}/series/{}".format(self.root, series_id)
                episode["series"] = self._cache[series_id] = self.request(
                    url, headers=headers).json()["data"]

            episode["date"] = text.parse_datetime(episode["publish_date"])
            yield Message.Directory, episode

            if episode["book"]:
                content, _ = text.extract(
                    html, '<div class="viewer">', '<div class="viewer-bottom')
                episode["num"] = 1
                episode["extension"] = "html"
                yield Message.Url, "text:" + content, episode

            else:  # comic
                for episode["num"], url in enumerate(text.extract_iter(
                        html, 'data-src="', '"'), 1):
                    yield Message.Url, url, text.nameext_from_url(url, episode)


class TapasSeriesExtractor(TapasExtractor):
    subcategory = "series"
    pattern = BASE_PATTERN + r"/series/([^/?#]+)"
    test = (
        ("https://tapas.io/series/just-leave-me-be", {
            "pattern": r"https://\w+\.cloudfront\.net/pc/\w\w/[0-9a-f-]+\.jpg",
            "count": 127,
        }),
        ("https://tapas.io/series/yona", {  # mature
            "count": 26,
        }),
    )

    def __init__(self, match):
        TapasExtractor.__init__(self, match)
        self.series_name = match.group(1)

    def episode_ids(self):
        url = "{}/series/{}".format(self.root, self.series_name)
        series_id, _, episode_id = text.extract(
            self.request(url).text, 'content="tapastic://series/', '"',
        )[0].partition("/episodes/")

        url = "{}/series/{}/episodes".format(self.root, series_id)
        headers = {"Accept": "application/json, text/javascript, */*;"}
        params = {
            "eid"        : episode_id,
            "page"       : 1,
            "sort"       : "OLDEST",
            "last_access": "0",
            "max_limit"  : "20",
        }

        while True:
            data = self.request(
                url, params=params, headers=headers).json()["data"]
            yield from text.extract_iter(
                data["body"], 'data-href="/episode/', '"')

            if not data["pagination"]["has_next"]:
                return
            params["page"] += 1


class TapasEpisodeExtractor(TapasExtractor):
    subcategory = "episode"
    pattern = BASE_PATTERN + r"/episode/(\d+)"
    test = ("https://tapas.io/episode/2068651", {
        "url": "0e536117dfaa17972e83d2e0141e6f9e91a33611",
        "pattern": "^text:",
        "keyword": {
            "book": True,
            "comment_cnt": int,
            "date": "dt:2021-02-23 16:02:07",
            "early_access": False,
            "escape_title": "You are a Tomb Raider (2)",
            "free": True,
            "id": 2068651,
            "like_cnt": int,
            "liked": bool,
            "mature": False,
            "next_ep_id": 2068652,
            "nsfw": False,
            "nu": False,
            "num": 1,
            "open_comments": True,
            "pending_scene": 2,
            "prev_ep_id": 2068650,
            "publish_date": "2021-02-23T16:02:07Z",
            "read": bool,
            "related_ep_id": None,
            "relative_publish_date": "Feb 23",
            "scene": 2,
            "scheduled": False,
            "title": "You are a Tomb Raider (2)",
            "unlock_cnt": 0,
            "unlocked": False,
            "view_cnt": 627,

            "series": {
                "genre": dict,
                "has_book_cover": True,
                "has_top_banner": True,
                "id": 199931,
                "premium": True,
                "sale_type": "PAID",
                "subscribed": bool,
                "thumbsup_cnt": int,
                "title": "Tomb Raider King",
                "type": "BOOKS",
                "url": "tomb-raider-king-novel",
            },
        },
    })

    def __init__(self, match):
        TapasExtractor.__init__(self, match)
        self.episode_id = match.group(1)

    def episode_ids(self):
        return (self.episode_id,)
