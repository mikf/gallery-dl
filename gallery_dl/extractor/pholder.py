# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pholder.com/"""

import json

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?pholder\.com"


def _thumb_resolution(thumbnail):
    try:
        return int(thumbnail["width"]) * int(thumbnail["height"])
    except ValueError:
        return 0


class PholderExtractor(Extractor):
    """Base class for pholder extractors"""
    category = "pholder"
    root = "https://pholder.com"
    directory_fmt = ("{category}", "{subredditTitle}")
    filename_fmt = "{id}{gallery_id:? / /}{title:? //[:225]}.{extension}"
    archive_fmt = "{id}_{filename}_{gallery_id:? / /}"
    request_interval = (2.0, 4.0)

    def __init__(self, match):
        Extractor.__init__(self, match)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)
        return response

    def _parse_window_data(self, html):
        # sometimes, window.data content is split across multiple script
        # blocks.
        tag_prefix = len("window_data = ")
        window_data_content = ""
        split_data = False

        for tag in text.split_html(html):
            if tag.startswith("window.data = "):
                try:
                    return util.json_loads(tag[tag_prefix:])
                except json.decoder.JSONDecodeError:
                    split_data = True

            if split_data:
                try:
                    window_data_content += tag
                    return util.json_loads(window_data_content[tag_prefix:])
                except json.decoder.JSONDecodeError:
                    pass

        raise exception.AbortExtraction("Could not locate window.data JSON.")

    def _posts(self, page_url):
        params = {"page": 1}
        while True:
            html = self.request(page_url, params=params).text
            window_data = self._parse_window_data(html)

            for item in window_data["media"]:
                data = {
                    "id": item["_id"],
                    "gallery_id": "",
                    "subredditTitle": item["_source"]["sub"],
                    "title": text.unquote(item["_source"]["title"]),
                    "tags": item["_source"]["tags"],
                }

                if ":" in data["id"]:
                    # this is a gallery
                    # (can also see from item["is_gallery"])
                    # pholder does not preserver gallery order, but assigns
                    # each image a sub-id.
                    data["id"], data["gallery_id"] = data["id"].partition(":")

                yield Message.Directory, "", data

                for thumb in sorted(
                        item["_source"]["thumbnails"],
                        key=lambda e: _thumb_resolution(e), reverse=True):
                    # try to use highest-resolution URLs from thumbnails first.
                    url = thumb["url"]
                    if url.rindex(":") > url.index(":"):
                        # sometimes, thumbnail image URLs end with ":large" or
                        # ":small", so we have to strip out any trailing
                        # ":word" bits.
                        url = url.rpartition(":")[0]
                    data["extension"] = text.ext_from_url(url)
                    yield Message.Url, url, data
                    break
                else:
                    # Fallback to origin
                    url = item["_source"]["origin"]
                    data["extension"] = text.ext_from_url(url)
                    yield Message.Url, url, data

            if len(window_data["media"]) < 150:
                break

            params["page"] += 1

    def items(self):
        url = f"{self.root}/{self.groups[0]}"
        yield from self._posts(url)


class PholderSubredditExtractor(PholderExtractor):
    """Extractor for media from pholder-stored posts for a subreddit"""
    subcategory = "subreddit"
    pattern = BASE_PATTERN + r"(/r/([^/?#]+))(?:/?\?([^#]+))?"
    example = "https://pholder.com/r/SUBREDDIT"


class PholderUserExtractor(PholderExtractor):
    """Extractor for URLs from pholder-stored posts for a reddit user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"(/u/[^/?#]+)(?:/?\?([^#]+))?"
    example = "https://www.pholder.com/u/USER"


class PholderSearchExtractor(PholderExtractor):
    """Extractor for URLs from pholder-stored posts for a search"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(.*)"
    example = "https://www.pholder.com/SEARCH"
