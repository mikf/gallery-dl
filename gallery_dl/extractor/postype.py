# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.postype.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?postype\.com"


class PostypeExtractor(Extractor):
    """Base class for postype extractors"""
    category = "postype"
    root = "https://www.postype.com"
    root_api = "https://api.postype.com"
    directory_fmt = ("{category}", "{channel[name]}")
    filename_fmt = "{post_id}_{num:>03}.{extension}"
    archive_fmt = "{post_id}_{num}"
    request_interval = (1.0, 2.0)

    def _call(self, endpoint, params=None):
        url = self.root_api + endpoint
        return self.request(url, params=params).json()

    def _extract_images(self, post_id):
        """Extract image URLs from post HTML content"""
        data = self._call("/api/v1/post/content/" + str(post_id))
        html = data["data"]["html"]

        images = []
        seen = set()

        for tag in text.extract_iter(html, "data-full-path=\"", "\""):
            url = text.unescape(tag)
            if url in seen:
                continue
            seen.add(url)

            # find surrounding context for dimensions
            idx = html.find(url)
            start = max(0, idx - 200)
            ctx = html[start:idx + len(url) + 10]

            w = text.extr(ctx, 'data-width="', '"')
            h = text.extr(ctx, 'data-height="', '"')

            images.append({
                "url"   : url,
                "width" : text.parse_int(w),
                "height": text.parse_int(h),
            })

        return images

    def _channel_by_name(self, channel_name):
        return self._call(
            "/api/v1/channels/by/channel-name/" + channel_name)

    def _post_info(self, post_id):
        """Fetch post metadata from API"""
        meta = self._call("/api/v1/posts/" + str(post_id))
        return {
            "channel" : meta["channel"],
            "title"   : meta["title"],
            "subtitle": meta.get("subTitle") or "",
            "date"    : self.parse_timestamp(
                meta["publishedAt"]),
            "tags"    : meta.get("tags") or [],
            "series"  : meta.get("series"),
            "views"   : meta["viewCount"],
            "likes"   : meta["likeCount"],
            "comments": meta["commentCount"],
            "price"   : meta["price"],
            "adult"   : meta.get("adult", False),
        }


class PostypePostExtractor(PostypeExtractor):
    """Extractor for a single postype post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/post/(\d+)"
    example = "https://www.postype.com/@USER/post/12345"

    def items(self):
        channel_name, post_id = self.groups

        post_info = self._post_info(post_id)
        images = self._extract_images(post_id)

        data = {
            **post_info,
            "post_id": text.parse_int(post_id),
            "count"  : len(images),
        }

        yield Message.Directory, "", data
        for data["num"], image in enumerate(images, 1):
            url = image["url"]
            data["width"] = image.get("width")
            data["height"] = image.get("height")
            yield Message.Url, url, text.nameext_from_url(url, data)


class PostypeChannelExtractor(PostypeExtractor):
    """Extractor for all posts of a postype channel"""
    subcategory = "channel"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/?$"
    example = "https://www.postype.com/@USER"

    def items(self):
        channel_name = self.groups[0]
        channel = self._channel_by_name(channel_name)
        channel_id = channel["channelId"]

        data = {"_extractor": PostypePostExtractor}

        for post in self._pagination(channel_id):
            post_id = post["postId"]
            url = "{0}/@{1}/post/{2}".format(
                self.root, channel_name, post_id)
            yield Message.Queue, url, data

    def _pagination(self, channel_id):
        endpoint = "/api/v2/channel/{}/activity/all".format(channel_id)
        page = 0

        while True:
            data = self._call(endpoint, {"page": page})

            for item in data["content"]:
                if item["type"] == "POST":
                    yield item["feedItem"]

            if data["last"]:
                return
            page += 1
