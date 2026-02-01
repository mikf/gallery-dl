# -*- coding: utf-8 -*-

# Copyright 2016-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://members.luscious.net/"""

from .common import Extractor, Message
from .. import text, exception


class LusciousExtractor(Extractor):
    """Base class for luscious extractors"""
    category = "luscious"
    cookies_domain = ".luscious.net"
    root = "https://members.luscious.net"

    def _request_graphql(self, opname, variables):
        data = {
            "id"           : 1,
            "operationName": opname,
            "query"        : self.utils("graphql", opname),
            "variables"    : variables,
        }
        response = self.request(
            f"{self.root}/graphql/nobatch/?operationName={opname}",
            method="POST", json=data, fatal=False,
        )

        if response.status_code >= 400:
            self.log.debug("Server response: %s", response.text)
            raise exception.AbortExtraction(
                f"GraphQL query failed "
                f"('{response.status_code} {response.reason}')")

        return response.json()["data"]


class LusciousAlbumExtractor(LusciousExtractor):
    """Extractor for image albums from luscious.net"""
    subcategory = "album"
    filename_fmt = "{category}_{album[id]}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{album[id]} {album[title]}")
    archive_fmt = "{album[id]}_{id}"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/(?:albums|pictures/c/[^/?#]+/album)/[^/?#]+_(\d+)")
    example = "https://luscious.net/albums/TITLE_12345/"

    def _init(self):
        self.album_id = self.groups[0]
        self.gif = self.config("gif", False)

    def items(self):
        album = self.metadata()
        yield Message.Directory, "", {"album": album}
        for num, image in enumerate(self.images(), 1):
            image["num"] = num
            image["album"] = album

            try:
                image["thumbnail"] = image.pop("thumbnails")[0]["url"]
            except LookupError:
                image["thumbnail"] = ""

            image["tags"] = [item["text"] for item in image["tags"]]
            image["date"] = self.parse_timestamp(image["created"])
            image["id"] = text.parse_int(image["id"])

            url = (image["url_to_original"] or image["url_to_video"]
                   if self.gif else
                   image["url_to_video"] or image["url_to_original"])

            yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        variables = {
            "id": self.album_id,
        }

        album = self._request_graphql("AlbumGet", variables)["album"]["get"]
        if "errors" in album:
            raise exception.NotFoundError("album")

        album["audiences"] = [item["title"] for item in album["audiences"]]
        album["genres"] = [item["title"] for item in album["genres"]]
        album["tags"] = [item["text"] for item in album["tags"]]

        album["cover"] = album["cover"]["url"]
        album["content"] = album["content"]["title"]
        album["language"] = album["language"]["title"].partition(" ")[0]
        album["created_by"] = album["created_by"]["display_name"]

        album["id"] = text.parse_int(album["id"])
        album["date"] = self.parse_timestamp(album["created"])

        return album

    def images(self):
        variables = {
            "input": {
                "filters": [{
                    "name" : "album_id",
                    "value": self.album_id,
                }],
                "display": "position",
                "page"   : 1,
            },
        }

        while True:
            data = self._request_graphql("AlbumListOwnPictures", variables)
            yield from data["picture"]["list"]["items"]

            if not data["picture"]["list"]["info"]["has_next_page"]:
                return
            variables["input"]["page"] += 1


class LusciousSearchExtractor(LusciousExtractor):
    """Extractor for album searches on luscious.net"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.|members\.)?luscious\.net"
               r"/albums/list/?(?:\?([^#]+))?")
    example = "https://luscious.net/albums/list/?tagged=TAG"

    def items(self):
        query = text.parse_query(self.groups[0])
        display = query.pop("display", "date_newest")
        page = query.pop("page", None)

        variables = {
            "input": {
                "display": display,
                "filters": [{"name": n, "value": v} for n, v in query.items()],
                "page": text.parse_int(page, 1),
            },
        }

        while True:
            data = self._request_graphql("AlbumListWithPeek", variables)

            for album in data["album"]["list"]["items"]:
                album["url"] = self.root + album["url"]
                album["_extractor"] = LusciousAlbumExtractor
                yield Message.Queue, album["url"], album

            if not data["album"]["list"]["info"]["has_next_page"]:
                return
            variables["input"]["page"] += 1
