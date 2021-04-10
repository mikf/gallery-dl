# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.fanbox.cc/"""

from .common import Extractor, Message
from .. import text


class FanboxExtractor(Extractor):
    """Base class for fanbox extractors"""
    category = "fanbox"
    root = "https://www.fanbox.cc"
    directory_fmt = ("{category}", "{creator_id}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"
    _warning = True

    def items(self):
        yield Message.Version, 1

        if self._warning:
            if "FANBOXSESSID" not in self.session.cookies:
                self.log.warning("no 'FANBOXSESSID' cookie set")
            FanboxExtractor._warning = False

        for url, data in self.posts():
            yield Message.Directory, data
            yield Message.Url, url, data

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, url):
        headers = {"Origin": self.root}

        while url:
            url = text.ensure_http_scheme(url)
            body = self.request(url, headers=headers).json()["body"]
            for item in body["items"]:
                for url, data in self._get_post_data_and_urls(item["id"]):
                    yield url, data

            url = body["nextUrl"]

    def _get_post_data_and_urls(self, post_id):
        """Fetch and process post data"""
        headers = {"Origin": self.root}
        url = "https://api.fanbox.cc/post.info?postId="+post_id
        pbody = self.request(url, headers=headers).json()["body"]

        post = {
            "id": pbody["id"],
            "title": pbody["title"],
            "fee_required": pbody["feeRequired"],
            "published": pbody["publishedDatetime"],
            "updated": pbody["updatedDatetime"],
            "type": pbody["type"],
            "tags": pbody["tags"],
            "creator_id": pbody["creatorId"],
            "has_adult_content": pbody["hasAdultContent"],
            "post_url": self.root+"/@"+pbody["creatorId"]+"/posts/"+post_id,
            "creator_user_id": pbody["user"]["userId"],
            "creator_name": pbody["user"]["name"],
            "text": pbody["body"].get("text", None) if pbody["body"] else None,
            "is_cover_image": False
        }

        num = 0
        if "coverImageUrl" in pbody and pbody["coverImageUrl"]:
            final_post = dict(post)
            final_post["isCoverImage"] = True
            final_post["file_url"] = pbody["coverImageUrl"]
            final_post = text.nameext_from_url(
                pbody["coverImageUrl"], final_post
            )
            final_post["num"] = num
            num += 1
            yield pbody["coverImageUrl"], final_post

        for group in ["images", "imageMap"]:
            if group in (pbody["body"] or []):
                for item in pbody["body"][group]:
                    final_post = dict(post)
                    final_post["file_url"] = item["originalUrl"]
                    final_post = text.nameext_from_url(
                        item["originalUrl"], final_post
                    )
                    if "extension" in item:
                        final_post["extension"] = item["extension"]
                    final_post["file_id"] = item.get("id", None)
                    final_post["width"] = item.get("width", None)
                    final_post["height"] = item.get("height", None)
                    final_post["num"] = num
                    num += 1
                    yield item["originalUrl"], final_post

        for group in ["files", "fileMap"]:
            if group in (pbody["body"] or []):
                for item in pbody["body"][group]:
                    final_post = dict(post)
                    final_post["file_url"] = item["url"]
                    final_post = text.nameext_from_url(item["url"], final_post)
                    if "extension" in item:
                        final_post["extension"] = item["extension"]
                    if "name" in item:
                        final_post["filename"] = item["name"]
                    final_post["file_id"] = item.get("id", None)
                    final_post["num"] = num
                    num += 1
                    yield item["url"], final_post


class FanboxCreatorExtractor(FanboxExtractor):
    """Extractor for a fanbox creator's works"""
    subcategory = "creator"
    pattern = (r"(?:https?://)?([a-zA-Z0-9_-]+)\.fanbox\.cc/?$|"
               r"(?:https?://)?(?:www\.)?fanbox\.cc/@([^/?#]+)/?$")
    test = (
        ("https://xub.fanbox.cc", {
            "range": "1-15",
            "count": ">= 15",
            "keyword": {
                "creator_id" : "xub",
                "tags"       : list,
                "title"      : str,
            },
        }),
    )

    def __init__(self, match):
        FanboxExtractor.__init__(self, match)
        self.creator_id = match.group(1) or match.group(2)

    def posts(self):
        url = "https://api.fanbox.cc/post.listCreator?creatorId={}&limit=10"

        return self._pagination(url.format(self._creator_id))


class FanboxPostExtractor(FanboxExtractor):
    """Extractor for media from a single fanbox post"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?fanbox\.cc/@[^/?#]+/posts/([^/?#]+)|"
               r"(?:https?://)?[a-zA-Z0-9_-]+\.fanbox\.cc/posts/([^/?#]+)")
    test = (
        ("https://www.fanbox.cc/@xub/posts/1910054", {
            "count": 3,
            "keyword": {
                "title": "えま★おうがすと",
                "tags": list,
                "has_adult_content": True,
                "is_cover_image": False
            },
        }),
    )

    def __init__(self, match):
        FanboxExtractor.__init__(self, match)
        self.post_id = match.group(1) or match.group(2)

    def posts(self):
        return self._get_post_data_and_urls(self.post_id)
