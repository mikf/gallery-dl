# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Gelbooru v0.1 sites"""

from . import booru
from .. import text


class GelbooruV01Extractor(booru.BooruExtractor):
    basecategory = "gelbooru_v01"
    per_page = 20

    def _parse_post(self, post_id):
        url = "{}/index.php?page=post&s=view&id={}".format(
            self.root, post_id)
        page = self.request(url).text

        post = text.extract_all(page, (
            ("created_at", 'Posted: ', ' <'),
            ("uploader"  , 'By: ', ' <'),
            ("width"     , 'Size: ', 'x'),
            ("height"    , '', ' <'),
            ("source"    , 'Source: <a href="', '"'),
            ("rating"    , 'Rating: ', '<'),
            ("score"     , 'Score: ', ' <'),
            ("file_url"  , '<img alt="img" src="', '"'),
            ("tags"      , 'id="tags" name="tags" cols="40" rows="5">', '<'),
        ))[0]

        post["id"] = post_id
        post["md5"] = post["file_url"].rpartition("/")[2].partition(".")[0]
        post["rating"] = (post["rating"] or "?")[0].lower()
        post["tags"] = text.unescape(post["tags"])
        post["date"] = text.parse_datetime(
            post["created_at"], "%Y-%m-%d %H:%M:%S")

        return post


BASE_PATTERN = GelbooruV01Extractor.update({
    "thecollection"     : {"root": "https://the-collection.booru.org"},
    "illusioncardsbooru": {"root": "https://illusioncards.booru.org"},
    "allgirlbooru"      : {"root": "https://allgirl.booru.org"},
    "drawfriends"       : {"root": "https://drawfriends.booru.org"},
    "vidyart"           : {"root": "https://vidyart.booru.org"},
    "theloudbooru"      : {"root": "https://tlb.booru.org"},
})


class GelbooruV01TagExtractor(GelbooruV01Extractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=list&tags=([^&#]+)"
    test = (
        (("https://the-collection.booru.org"
          "/index.php?page=post&s=list&tags=parody"), {
            "range": "1-25",
            "count": 25,
        }),
        (("https://illusioncards.booru.org"
          "/index.php?page=post&s=list&tags=koikatsu"), {
            "range": "1-25",
            "count": 25,
        }),
        ("https://allgirl.booru.org/index.php?page=post&s=list&tags=dress", {
            "range": "1-25",
            "count": 25,
        }),
        ("https://drawfriends.booru.org/index.php?page=post&s=list&tags=all"),
        ("https://vidyart.booru.org/index.php?page=post&s=list&tags=all"),
        ("https://tlb.booru.org/index.php?page=post&s=list&tags=all"),
    )

    def __init__(self, match):
        GelbooruV01Extractor.__init__(self, match)
        self.tags = match.group(match.lastindex)

    def metadata(self):
        return {"search_tags": text.unquote(self.tags.replace("+", " "))}

    def posts(self):
        url = "{}/index.php?page=post&s=list&tags={}&pid=".format(
            self.root, self.tags)
        pid = self.page_start

        while True:
            page = self.request(url + str(pid)).text

            cnt = 0
            for post_id in text.extract_iter(
                    page, 'class="thumb"><a id="p', '"'):
                yield self._parse_post(post_id)
                cnt += 1

            if cnt < self.per_page:
                return
            pid += self.per_page


class GelbooruV01PostExtractor(GelbooruV01Extractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=view&id=(\d+)"
    test = (
        (("https://the-collection.booru.org"
          "/index.php?page=post&s=view&id=100520"), {
            "url": "0329ac8588bb93cf242ca0edbe3e995b4ba554e8",
            "content": "1e585874e7b874f7937df1060dd1517fef2f4dfb",
        }),
        (("https://illusioncards.booru.org"
          "/index.php?page=post&s=view&id=82746"), {
            "url": "3f9cd2fadf78869b90bc5422f27b48f1af0e0909",
            "content": "159e60b92d05597bd1bb63510c2c3e4a4bada1dc",
        }),
        ("https://allgirl.booru.org/index.php?page=post&s=view&id=107213", {
            "url": "b416800d2d2b072f80d3b37cfca9cb806fb25d51",
            "content": "3e3c65e0854a988696e11adf0de52f8fa90a51c7",
            "keyword": {
                "created_at": "2021-02-13 16:27:39",
                "date": "dt:2021-02-13 16:27:39",
                "file_url": "https://img.booru.org/allgirl//images/107"
                            "/2aaa0438d58fc7baa75a53b4a9621bb89a9d3fdb.jpg",
                "height": "1200",
                "id": "107213",
                "md5": "2aaa0438d58fc7baa75a53b4a9621bb89a9d3fdb",
                "rating": "s",
                "score": str,
                "source": None,
                "tags": "blush dress green_eyes green_hair hatsune_miku "
                        "long_hair twintails vocaloid",
                "uploader": "Honochi31",
                "width": "1600"
            },
        }),
        ("https://drawfriends.booru.org/index.php?page=post&s=view&id=107474"),
        ("https://vidyart.booru.org/index.php?page=post&s=view&id=383111"),
        ("https://tlb.booru.org/index.php?page=post&s=view&id=127223"),
    )

    def __init__(self, match):
        GelbooruV01Extractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        return (self._parse_post(self.post_id),)
