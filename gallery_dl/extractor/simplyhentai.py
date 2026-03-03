# -*- coding: utf-8 -*-

# Copyright 2018-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.simply-hentai.com/"""

from .common import Extractor, GalleryExtractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?simply-hentai\.com"


class SimplyhentaiExtractor(Extractor):
    """Base class for simplyhentai extractors"""
    category = "simplyhentai"
    root = "https://www.simply-hentai.com"
    root_api = "https://api-v3.simply-hentai.com"

    def items(self):
        for gallery in self.galleries():
            gallery["_extractor"] = SimplyhentaiGalleryExtractor
            series = (s["slug"] if (s := gallery.get("series")) else
                      "8-original-work")
            url = f"{self.root}/{series}/{gallery['slug']}"
            yield Message.Queue, url, gallery

    def request_api(self, endpoint, params=None):
        url = f"{self.root_api}/v3{endpoint}"
        return self.request_json(url, params=params, headers={
            "Referer": self.root + "/",
            "Origin" : self.root,
        })

    def _pagination(self, endpoint, params):
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            data = self.request_api(endpoint, params)

            if isinstance(data["data"], dict):
                yield from data["data"]["albums"]
            else:
                yield from data["data"]

            try:
                if params["page"] >= data["pagination"]["pages"]:
                    break
            except Exception:
                break
            params["page"] += 1


class SimplyhentaiSeriesExtractor(SimplyhentaiExtractor):
    subcategory = "series"
    pattern = (BASE_PATTERN + r"/series/([^/?#]+)"
               r"(?:/tag-([^/?#]+))?(?:/sort-([^/?#]+))?(?:/page-(\d+))?"
               r"(?:\?([^#]+))?")
    example = "https://www.simply-hentai.com/series/SLUG"

    def galleries(self):
        slug, tag, sort, pnum, qs = self.groups
        params = text.parse_query(qs)
        if tag is not None:
            params["tag_slug"] = tag
        if sort is not None:
            params["sort"] = sort
        if pnum is not None:
            params["page"] = pnum
        return self._pagination(f"/series/{slug}", params)


class SimplyhentaiMangaExtractor(SimplyhentaiExtractor):
    subcategory = "manga"
    pattern = (BASE_PATTERN + r"/2-mangas"
               r"(?:/sort-([^/?#]+))?(?:/page-(\d+))?(?:\?([^#]+))?")
    example = "https://www.simply-hentai.com/2-mangas"

    def galleries(self):
        sort, pnum, qs = self.groups
        params = text.parse_query(qs)
        if sort is not None:
            params["sort"] = sort
        if pnum is not None:
            params["page"] = pnum
        return self._pagination("/mangas", params)


class SimplyhentaiTagExtractor(SimplyhentaiExtractor):
    subcategory = "tag"
    pattern = (BASE_PATTERN +
               r"/(parody|tag|character|collection|artist|translator)"
               r"/([^/?#]+)"
               r"(?:/tag-([^/?#]+))?(?:/sort-([^/?#]+))?(?:/page-(\d+))?"
               r"(?:\?([^#]+))?")
    example = "https://www.simply-hentai.com/tag/TAG"

    def galleries(self):
        type, slug, tag, sort, pnum, qs = self.groups
        params = text.parse_query(qs)
        if type == "collection":
            endpoint = "/collection/" + slug
        else:
            endpoint = "/tag/" + slug
            params["type"] = type
        if tag is not None:
            params["tag_slug"] = tag
        if sort is not None:
            params["sort"] = sort
        if pnum is not None:
            params["page"] = pnum
        return self._pagination(endpoint, params)


class SimplyhentaiLanguageExtractor(SimplyhentaiExtractor):
    subcategory = "language"
    pattern = (BASE_PATTERN + r"/language/([^/?#]+)"
               r"(?:/sort-([^/?#]+))?(?:/page-(\d+))?(?:\?([^#]+))?")
    example = "https://www.simply-hentai.com/language/LANG"

    def galleries(self):
        language, sort, pnum, qs = self.groups
        params = text.parse_query(qs)
        params["type"] = "language"
        if sort is not None:
            params["sort"] = sort
        if pnum is not None:
            params["page"] = pnum
        return self._pagination(f"/tag/{language}", params)


class SimplyhentaiGalleryExtractor(GalleryExtractor, SimplyhentaiExtractor):
    """Extractor for simplyhentai galleries"""
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/[^/?#]+/([^/?#]+)"
    example = "https://www.simply-hentai.com/SERIES/SLUG"

    def metadata(self, _):
        endpoint = "/manga/" + self.groups[0]
        data = self.request_api(endpoint)["data"]
        data["gallery_id"] = data.pop("id")
        data["series"] = (s := data.get("series")) and s.get("title")
        data["date"] = self.parse_datetime_iso(data.get("created_at"))

        for key in ("artists", "characters", "parodies",
                    "tags", "translators"):
            data[key] = [t["title"] for t in data.get(key) or ()]

        data.pop("related", None)
        self._images = data.pop("images", ())
        if data.get("image_count", 32) > 12:
            self._images = endpoint + "/pages"

        try:
            language = data["language"]["name"]
            data["lang"] = util.language_to_code(language)
            data["language"] = language
        except Exception:
            pass

        try:
            data["cover"] = data.pop("preview")["sizes"]["full"]
        except Exception:
            pass

        return data

    def images(self, _):
        imgs = self._images
        if isinstance(imgs, str):
            imgs = self.request_api(imgs)["data"]["pages"]
        return [(img["sizes"]["full"], {"id": img["id"]}) for img in imgs]
