# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.fanbox.cc/"""

from .common import Extractor, Message
from .. import text


BASE_PATTERN = (
    r"(?:https?://)?(?:"
    r"(?!www\.)([\w-]+)\.fanbox\.cc|"
    r"(?:www\.)?fanbox\.cc/@([\w-]+))"
)


class FanboxExtractor(Extractor):
    """Base class for Fanbox extractors"""
    category = "fanbox"
    root = "https://www.fanbox.cc"
    directory_fmt = ("{category}", "{creatorId}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"
    _warning = True

    def items(self):
        yield Message.Version, 1

        if self._warning:
            if "FANBOXSESSID" not in self.session.cookies:
                self.log.warning("no 'FANBOXSESSID' cookie set")
            FanboxExtractor._warning = False

        for content_body, post in self.posts():
            yield Message.Directory, post
            yield from self._get_urls_from_post(content_body, post)

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, url):
        headers = {"Origin": self.root}

        while url:
            url = text.ensure_http_scheme(url)
            body = self.request(url, headers=headers).json()["body"]
            for item in body["items"]:
                yield self._process_post(item)

            url = body["nextUrl"]

    def _get_post_data_from_id(self, post_id):
        """Fetch and process post data"""
        headers = {"Origin": self.root}
        url = "https://api.fanbox.cc/post.info?postId="+post_id
        post = self.request(url, headers=headers).json()["body"]

        return self._process_post(post)

    def _process_post(self, post):
        content_body = post.pop("body", None)
        post["date"] = text.parse_datetime(post["publishedDatetime"])
        post["text"] = content_body.get("text") if content_body else None
        post["isCoverImage"] = False

        return content_body, post

    def _get_urls_from_post(self, content_body, post):
        num = 0
        cover_image = post.get("coverImageUrl")
        if cover_image:
            final_post = post.copy()
            final_post["isCoverImage"] = True
            final_post["fileUrl"] = cover_image
            text.nameext_from_url(cover_image, final_post)
            final_post["num"] = num
            num += 1
            yield Message.Url, cover_image, final_post

        if not content_body:
            return

        for group in ("images", "imageMap"):
            if group in content_body:
                for item in content_body[group]:
                    final_post = post.copy()
                    final_post["fileUrl"] = item["originalUrl"]
                    text.nameext_from_url(item["originalUrl"], final_post)
                    if "extension" in item:
                        final_post["extension"] = item["extension"]
                    final_post["fileId"] = item.get("id")
                    final_post["width"] = item.get("width")
                    final_post["height"] = item.get("height")
                    final_post["num"] = num
                    num += 1
                    yield Message.Url, item["originalUrl"], final_post

        for group in ("files", "fileMap"):
            if group in content_body:
                for item in content_body[group]:
                    final_post = post.copy()
                    final_post["fileUrl"] = item["url"]
                    text.nameext_from_url(item["url"], final_post)
                    if "extension" in item:
                        final_post["extension"] = item["extension"]
                    if "name" in item:
                        final_post["filename"] = item["name"]
                    final_post["fileId"] = item.get("id")
                    final_post["num"] = num
                    num += 1
                    yield Message.Url, item["url"], final_post


class FanboxCreatorExtractor(FanboxExtractor):
    """Extractor for a Fanbox creator's works"""
    subcategory = "creator"
    pattern = BASE_PATTERN + r"(?:/posts)?/?$"
    test = (
        ("https://xub.fanbox.cc", {
            "range": "1-15",
            "count": ">= 15",
            "keyword": {
                "creatorId" : "xub",
                "tags"       : list,
                "title"      : str,
            },
        }),
        ("https://xub.fanbox.cc/posts"),
        ("https://www.fanbox.cc/@xub/"),
        ("https://www.fanbox.cc/@xub/posts"),
    )

    def __init__(self, match):
        FanboxExtractor.__init__(self, match)
        self.creator_id = match.group(1) or match.group(2)

    def posts(self):
        url = "https://api.fanbox.cc/post.listCreator?creatorId={}&limit=10"

        return self._pagination(url.format(self.creator_id))


class FanboxPostExtractor(FanboxExtractor):
    """Extractor for media from a single Fanbox post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    test = (
        ("https://www.fanbox.cc/@xub/posts/1910054", {
            "count": 3,
            "keyword": {
                "title": "えま★おうがすと",
                "tags": list,
                "hasAdultContent": True,
                "isCoverImage": False
            },
        }),
    )

    def __init__(self, match):
        FanboxExtractor.__init__(self, match)
        self.post_id = match.group(3)

    def posts(self):
        (self._get_post_data_from_id(self.post_id),)
