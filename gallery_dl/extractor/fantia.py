# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fantia.jp/"""

from .common import Extractor, Message
from .. import text


class FantiaExtractor(Extractor):
    """Base class for Fantia extractors"""
    category = "fantia"
    root = "https://fantia.jp"
    directory_fmt = ("{category}", "{fanclub_id}")
    filename_fmt = "{post_id}_{file_id}.{extension}"
    archive_fmt = "{post_id}_{file_id}"
    _warning = True

    def items(self):

        if self._warning:
            if "_session_id" not in self.session.cookies:
                self.log.warning("no '_session_id' cookie set")
            FantiaExtractor._warning = False

        for post_id in self.posts():
            full_response, post = self._get_post_data(post_id)
            yield Message.Directory, post
            for url, url_data in self._get_urls_from_post(full_response, post):
                fname = url_data["content_filename"] or url
                text.nameext_from_url(fname, url_data)
                url_data["file_url"] = url
                yield Message.Url, url, url_data

    def posts(self):
        """Return post IDs"""

    def _pagination(self, url):
        params = {"page": 1}
        headers = {"Referer": self.root}

        while True:
            page = self.request(url, params=params, headers=headers).text

            post_id = None
            for post_id in text.extract_iter(
                    page, 'class="link-block" href="/posts/', '"'):
                yield post_id

            if not post_id:
                return
            params["page"] += 1

    def _get_post_data(self, post_id):
        """Fetch and process post data"""
        headers = {"Referer": self.root}
        url = self.root+"/api/v1/posts/"+post_id
        resp = self.request(url, headers=headers).json()["post"]
        post = {
            "post_id": resp["id"],
            "post_url": self.root + "/posts/" + str(resp["id"]),
            "post_title": resp["title"],
            "comment": resp["comment"],
            "rating": resp["rating"],
            "posted_at": resp["posted_at"],
            "date": text.parse_datetime(
                resp["posted_at"], "%a, %d %b %Y %H:%M:%S %z"),
            "fanclub_id": resp["fanclub"]["id"],
            "fanclub_user_id": resp["fanclub"]["user"]["id"],
            "fanclub_user_name": resp["fanclub"]["user"]["name"],
            "fanclub_name": resp["fanclub"]["name"],
            "fanclub_url": self.root+"/fanclubs/"+str(resp["fanclub"]["id"]),
            "tags": resp["tags"]
        }
        return resp, post

    def _get_urls_from_post(self, resp, post):
        """Extract individual URL data from the response"""
        if "thumb" in resp and resp["thumb"] and "original" in resp["thumb"]:
            post["content_filename"] = ""
            post["content_category"] = "thumb"
            post["file_id"] = "thumb"
            yield resp["thumb"]["original"], post

        for content in resp["post_contents"]:
            post["content_category"] = content["category"]
            post["content_title"] = content["title"]
            post["content_filename"] = content.get("filename", "")
            post["content_id"] = content["id"]
            if "post_content_photos" in content:
                for photo in content["post_content_photos"]:
                    post["file_id"] = photo["id"]
                    yield photo["url"]["original"], post
            if "download_uri" in content:
                post["file_id"] = content["id"]
                yield self.root+"/"+content["download_uri"], post


class FantiaCreatorExtractor(FantiaExtractor):
    """Extractor for a Fantia creator's works"""
    subcategory = "creator"
    pattern = r"(?:https?://)?(?:www\.)?fantia\.jp/fanclubs/(\d+)"
    test = (
        ("https://fantia.jp/fanclubs/6939", {
            "range": "1-25",
            "count": ">= 25",
            "keyword": {
                "fanclub_user_id" : 52152,
                "tags"            : list,
                "title"           : str,
            },
        }),
    )

    def __init__(self, match):
        FantiaExtractor.__init__(self, match)
        self.creator_id = match.group(1)

    def posts(self):
        url = "{}/fanclubs/{}/posts".format(self.root, self.creator_id)
        return self._pagination(url)


class FantiaPostExtractor(FantiaExtractor):
    """Extractor for media from a single Fantia post"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?fantia\.jp/posts/(\d+)"
    test = (
        ("https://fantia.jp/posts/508363", {
            "count": 6,
            "keyword": {
                "post_title": "zunda逆バニーでおしりｺｯｼｮﾘ",
                "tags": list,
                "rating": "adult",
                "post_id": 508363
            },
        }),
    )

    def __init__(self, match):
        FantiaExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self.post_id,)
