# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Moebooru based sites"""

from .booru import BooruExtractor
from .. import text

import collections
import datetime
import re


class MoebooruExtractor(BooruExtractor):
    """Base class for Moebooru extractors"""
    basecategory = "moebooru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_start = 1

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_timestamp(post["created_at"])

    def _html(self, post):
        return self.request("{}/post/show/{}".format(
            self.root, post["id"])).text

    def _tags(self, post, page):
        tag_container = text.extr(page, '<ul id="tag-', '</ul>')
        if not tag_container:
            return

        tags = collections.defaultdict(list)
        pattern = re.compile(r"tag-type-([^\"' ]+).*?[?;]tags=([^\"'+]+)")
        for tag_type, tag_name in pattern.findall(tag_container):
            tags[tag_type].append(text.unquote(tag_name))
        for key, value in tags.items():
            post["tags_" + key] = " ".join(value)

    def _notes(self, post, page):
        note_container = text.extr(page, 'id="note-container"', "<img ")
        if not note_container:
            return

        post["notes"] = notes = []
        for note in note_container.split('class="note-box"')[1:]:
            extr = text.extract_from(note)
            notes.append({
                "width" : int(extr("width:", "p")),
                "height": int(extr("height:", "p")),
                "y"     : int(extr("top:", "p")),
                "x"     : int(extr("left:", "p")),
                "id"    : int(extr('id="note-body-', '"')),
                "body"  : text.unescape(text.remove_html(extr(">", "</div>"))),
            })

    def _pagination(self, url, params):
        params["page"] = self.page_start
        params["limit"] = self.per_page

        while True:
            posts = self.request(url, params=params).json()
            yield from posts

            if len(posts) < self.per_page:
                return
            params["page"] += 1


BASE_PATTERN = MoebooruExtractor.update({
    "yandere": {
        "root": "https://yande.re",
        "pattern": r"yande\.re",
    },
    "konachan": {
        "root": "https://konachan.com",
        "pattern": r"konachan\.(?:com|net)",
    },
    "sakugabooru": {
        "root": "https://www.sakugabooru.com",
        "pattern": r"(?:www\.)?sakugabooru\.com",
    },
    "lolibooru": {
        "root": "https://lolibooru.moe",
        "pattern": r"lolibooru\.moe",
    },
})


class MoebooruTagExtractor(MoebooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/post\?(?:[^&#]*&)*tags=([^&#]*)"
    example = "https://yande.re/post?tags=TAG"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        params = {"tags": self.tags}
        return self._pagination(self.root + "/post.json", params)


class MoebooruPoolExtractor(MoebooruExtractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/pool/show/(\d+)"
    example = "https://yande.re/pool/show/12345"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)

    def metadata(self):
        if self.config("metadata"):
            url = "{}/pool/show/{}.json".format(self.root, self.pool_id)
            pool = self.request(url).json()
            pool.pop("posts", None)
            return {"pool": pool}
        return {"pool": text.parse_int(self.pool_id)}

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination(self.root + "/post.json", params)


class MoebooruPostExtractor(MoebooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/show/(\d+)"
    example = "https://yande.re/post/show/12345"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        params = {"tags": "id:" + self.post_id}
        return self.request(self.root + "/post.json", params=params).json()


class MoebooruPopularExtractor(MoebooruExtractor):
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = BASE_PATTERN + \
        r"/post/popular_(by_(?:day|week|month)|recent)(?:\?([^#]*))?"
    example = "https://yande.re/post/popular_by_month?year=YYYY&month=MM"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.scale = match.group(match.lastindex-1)
        self.query = match.group(match.lastindex)

    def metadata(self):
        self.params = params = text.parse_query(self.query)

        if "year" in params:
            date = "{:>04}-{:>02}-{:>02}".format(
                params["year"],
                params.get("month", "01"),
                params.get("day", "01"),
            )
        else:
            date = datetime.date.today().isoformat()

        scale = self.scale
        if scale.startswith("by_"):
            scale = scale[3:]
        if scale == "week":
            date = datetime.date.fromisoformat(date)
            date = (date - datetime.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        url = "{}/post/popular_{}.json".format(self.root, self.scale)
        return self.request(url, params=self.params).json()
