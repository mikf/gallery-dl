# -*- coding: utf-8 -*-

# Copyright 2020-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .common import Extractor, Message
from .. import text


class RedgifsExtractor(Extractor):
    """Base class for redgifs extractors"""
    category = "redgifs"
    filename_fmt = \
        "{category}_{gallery:?//[:11]}{num:?_/_/>02}{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.redgifs.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match[1]

    def _init(self):
        self.api = self.utils().RedgifsAPI(self)

        formats = self.config("format")
        if formats is None:
            formats = ("hd", "sd", "gif")
        elif isinstance(formats, str):
            formats = (formats, "hd", "sd", "gif")
        self.formats = formats

    def items(self):
        metadata = self.metadata()

        for gif in self.gifs():

            if gallery := gif.get("gallery"):
                gifs = self.api.gallery(gallery)["gifs"]
                enum = 1
                cnt = len(gifs)
            else:
                gifs = (gif,)
                enum = 0
                cnt = 1

            gif.update(metadata)
            gif["count"] = cnt
            gif["date"] = self.parse_timestamp(gif.get("createDate"))
            yield Message.Directory, gif

            for num, gif in enumerate(gifs, enum):
                gif["_fallback"] = formats = self._formats(gif)
                url = next(formats, None)

                if not url:
                    self.log.warning(
                        "Skipping '%s' (format not available)", gif["id"])
                    continue

                gif["num"] = num
                gif["count"] = cnt
                yield Message.Url, url, gif

    def _formats(self, gif):
        urls = gif["urls"]
        for fmt in self.formats:
            if url := urls.get(fmt):
                url = url.replace("//thumbs2.", "//thumbs3.", 1)
                text.nameext_from_url(url, gif)
                yield url

    def metadata(self):
        return {}

    def gifs(self):
        return ()


class RedgifsUserExtractor(RedgifsExtractor):
    """Extractor for redgifs user profiles"""
    subcategory = "user"
    directory_fmt = ("{category}", "{userName}")
    pattern = (r"(?:https?://)?(?:\w+\.)?redgifs\.com/users/([^/?#]+)/?"
               r"(?:\?([^#]+))?$")
    example = "https://www.redgifs.com/users/USER"

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.query = match[2]

    def metadata(self):
        return {"userName": self.key}

    def gifs(self):
        order = text.parse_query(self.query).get("order")
        return self.api.user(self.key, order or "new")


class RedgifsCollectionExtractor(RedgifsExtractor):
    """Extractor for an individual user collection"""
    subcategory = "collection"
    directory_fmt = (
        "{category}", "{collection[userName]}", "{collection[folderName]}")
    archive_fmt = "{collection[folderId]}_{id}"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/users"
               r"/([^/?#]+)/collections/([^/?#]+)")
    example = "https://www.redgifs.com/users/USER/collections/ID"

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.collection_id = match[2]

    def metadata(self):
        collection = self.api.collection_info(self.key, self.collection_id)
        collection["userName"] = self.key
        return {"collection": collection}

    def gifs(self):
        return self.api.collection(self.key, self.collection_id)


class RedgifsCollectionsExtractor(RedgifsExtractor):
    """Extractor for redgifs user collections"""
    subcategory = "collections"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/users"
               r"/([^/?#]+)/collections/?$")
    example = "https://www.redgifs.com/users/USER/collections"

    def items(self):
        base = f"{self.root}/users/{self.key}/collections/"
        for collection in self.api.collections(self.key):
            url = f"{base}{collection['folderId']}"
            collection["_extractor"] = RedgifsCollectionExtractor
            yield Message.Queue, url, collection


class RedgifsNichesExtractor(RedgifsExtractor):
    """Extractor for redgifs niches"""
    subcategory = "niches"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/niches/([^/?#]+)/?"
               r"(?:\?([^#]+))?$")
    example = "https://www.redgifs.com/niches/NAME"

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.query = match[2]

    def gifs(self):
        order = text.parse_query(self.query).get("order")
        return self.api.niches(self.key, order or "new")


class RedgifsSearchExtractor(RedgifsExtractor):
    """Extractor for redgifs search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = (r"(?:https?://)?(?:\w+\.)?redgifs\.com"
               r"/(?:gifs/([^/?#]+)|search(?:/gifs)?()|browse)"
               r"(?:/?\?([^#]+))?")
    example = "https://www.redgifs.com/gifs/TAG"

    def metadata(self):
        tag, self.search, query = self.groups

        self.params = params = text.parse_query(query)
        if tag is not None:
            params["tags"] = text.unquote(tag)

        return {"search": (params.get("query") or
                           params.get("tags") or
                           params.get("order") or
                           "trending")}

    def gifs(self):
        if self.search is None:
            return self.api.gifs_search(self.params)
        else:
            return self.api.search_gifs(self.params)


class RedgifsImageExtractor(RedgifsExtractor):
    """Extractor for individual gifs from redgifs.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:\w+\.)?redgifs\.com/(?:watch|ifr)|"
               r"(?:\w+\.)?gfycat\.com(?:/gifs/detail|/\w+)?|"
               r"(?:www\.)?gifdeliverynetwork\.com|"
               r"i\.redgifs\.com/i)/([A-Za-z0-9]+)")
    example = "https://redgifs.com/watch/ID"

    def gifs(self):
        return (self.api.gif(self.key),)
