# -*- coding: utf-8 -*-

# Copyright 2020-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Moebooru based sites"""

from .booru import BooruExtractor
from .. import text, dt
import collections


class MoebooruExtractor(BooruExtractor):
    """Base class for Moebooru extractors"""
    basecategory = "moebooru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_start = 1

    def _prepare(self, post):
        post["date"] = dt.parse_ts(post["created_at"])

    def _html(self, post):
        url = f"{self.root}/post/show/{post['id']}"
        return self.request(url).text

    def _tags(self, post, page):
        tag_container = text.extr(page, '<ul id="tag-', '</ul>')
        if not tag_container:
            return

        tags = collections.defaultdict(list)
        pattern = text.re(r"tag-type-([^\"' ]+).*?[?;]tags=([^\"'+]+)")
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
            posts = self.request_json(url, params=params)
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
    pattern = rf"{BASE_PATTERN}/post\?(?:[^&#]*&)*tags=([^&#]*)"
    example = "https://yande.re/post?tags=TAG"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.tags = text.unquote(self.groups[-1].replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        params = {"tags": self.tags}
        return self._pagination(f"{self.root}/post.json", params)


class MoebooruPoolExtractor(MoebooruExtractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = rf"{BASE_PATTERN}/pool/show/(\d+)"
    example = "https://yande.re/pool/show/12345"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.pool_id = self.groups[-1]

    def metadata(self):
        if self.config("metadata"):
            url = f"{self.root}/pool/show/{self.pool_id}.json"
            pool = self.request_json(url)
            pool["name"] = pool["name"].replace("_", " ")
            pool.pop("posts", None)
            return {"pool": pool}
        return {"pool": text.parse_int(self.pool_id)}

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination(f"{self.root}/post.json", params)


class MoebooruPostExtractor(MoebooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = rf"{BASE_PATTERN}/post/show/(\d+)"
    example = "https://yande.re/post/show/12345"

    def posts(self):
        params = {"tags": "id:" + self.groups[-1]}
        return self.request_json(f"{self.root}/post.json", params=params)


class MoebooruPopularExtractor(MoebooruExtractor):
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = (rf"{BASE_PATTERN}"
               rf"/post/popular_(by_(?:day|week|month)|recent)(?:\?([^#]*))?")
    example = "https://yande.re/post/popular_by_month?year=YYYY&month=MM"

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.scale = self.groups[-2]
        self.query = self.groups[-1]

    def metadata(self):
        self.params = params = text.parse_query(self.query)

        if "year" in params:
            date = (f"{params['year']:>04}-{params.get('month', '01'):>02}-"
                    f"{params.get('day', '01'):>02}")
        else:
            date = dt.date.today().isoformat()

        scale = self.scale
        if scale.startswith("by_"):
            scale = scale[3:]
        if scale == "week":
            date = dt.date.fromisoformat(date)
            date = (date - dt.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        url = f"{self.root}/post/popular_{self.scale}.json"
        return self.request_json(url, params=self.params)
