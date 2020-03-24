# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://35photo.pro/"""

from .common import Extractor, Message
from .. import text


class _35photoExtractor(Extractor):
    category = "35photo"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{id}{title:?_//}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    root = "https://35photo.pro"

    def items(self):
        first = True
        data = self.metadata()
        yield Message.Version, 1

        for photo_id in self.photos():
            for photo in self._photo_data(photo_id):
                photo.update(data)
                url = photo["url"]
                if first:
                    first = False
                    yield Message.Directory, photo
                yield Message.Url, url, text.nameext_from_url(url, photo)

    def metadata(self):
        """Returns general metadata"""
        return {}

    def photos(self):
        """Returns an iterable containing all relevant photo IDs"""

    def _pagination(self, params, extra_ids=None):
        url = "https://35photo.pro/show_block.php"
        headers = {"Referer": self.root, "X-Requested-With": "XMLHttpRequest"}
        params["type"] = "getNextPageData"

        if "lastId" not in params:
            params["lastId"] = "999999999"
        if extra_ids:
            yield from extra_ids
        while params["lastId"]:
            data = self.request(url, headers=headers, params=params).json()
            yield from self._photo_ids(data["data"])
            params["lastId"] = data["lastId"]

    def _photo_data(self, photo_id):
        params = {"method": "photo.getData", "photoId": photo_id}
        data = self.request(
            "https://api.35photo.pro/", params=params).json()["data"][photo_id]
        info = {
            "url"        : data["src"],
            "id"         : data["photo_id"],
            "title"      : data["photo_name"],
            "description": data["photo_desc"],
            "tags"       : data["tags"] or [],
            "views"      : data["photo_see"],
            "favorites"  : data["photo_fav"],
            "score"      : data["photo_rating"],
            "type"       : data["photo_type"],
            "date"       : data["timeAdd"],
            "user"       : data["user_login"],
            "user_id"    : data["user_id"],
            "user_name"  : data["user_name"],
        }

        if "series" in data:
            for info["num"], photo in enumerate(data["series"], 1):
                info["url"] = photo["src"]
                info["id_series"] = text.parse_int(photo["id"])
                info["title_series"] = photo["title"] or ""
                yield info.copy()
        else:
            info["num"] = 1
            yield info

    @staticmethod
    def _photo_ids(page):
        """Extract unique photo IDs and return them as sorted list"""
        #  searching for photo-id="..." doesn't always work (see unit tests)
        if not page:
            return ()
        return sorted(
            set(text.extract_iter(page, "/photo_", "/")),
            key=text.parse_int,
            reverse=True,
        )


class _35photoUserExtractor(_35photoExtractor):
    """Extractor for all images of a user on 35photo.pro"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:[a-z]+\.)?35photo\.pro"
               r"/(?!photo_|genre_|tags/|rating/)([^/?&#]+)")
    test = (
        ("https://35photo.pro/liya", {
            "pattern": r"https://m\d+.35photo.pro/photos_(main|series)/.*.jpg",
            "count": 9,
        }),
        ("https://35photo.pro/suhoveev", {
            # last photo ID (1267028) isn't given as 'photo-id="<id>"
            # there are only 23 photos without the last one
            "count": ">= 33",
        }),
        ("https://en.35photo.pro/liya"),
        ("https://ru.35photo.pro/liya"),
    )

    def __init__(self, match):
        _35photoExtractor.__init__(self, match)
        self.user = match.group(1)
        self.user_id = 0

    def metadata(self):
        url = "{}/{}/".format(self.root, self.user)
        page = self.request(url).text
        self.user_id = text.parse_int(text.extract(page, "/user_", ".xml")[0])
        return {
            "user": self.user,
            "user_id": self.user_id,
        }

    def photos(self):
        return self._pagination({
            "page": "photoUser",
            "user_id": self.user_id,
        })


class _35photoTagExtractor(_35photoExtractor):
    """Extractor for all photos from a tag listing"""
    subcategory = "tag"
    directory_fmt = ("{category}", "Tags", "{search_tag}")
    archive_fmt = "t{search_tag}_{id}_{num}"
    pattern = r"(?:https?://)?(?:[a-z]+\.)?35photo\.pro/tags/([^/?&#]+)"
    test = ("https://35photo.pro/tags/landscape/", {
        "range": "1-25",
        "count": 25,
    })

    def __init__(self, match):
        _35photoExtractor.__init__(self, match)
        self.tag = match.group(1)

    def metadata(self):
        return {"search_tag": text.unquote(self.tag).lower()}

    def photos(self):
        num = 1

        while True:
            url = "{}/tags/{}/list_{}/".format(self.root, self.tag, num)
            page = self.request(url).text
            prev = None

            for photo_id in text.extract_iter(page, "35photo.pro/photo_", "/"):
                if photo_id != prev:
                    prev = photo_id
                    yield photo_id

            if not prev:
                return
            num += 1


class _35photoGenreExtractor(_35photoExtractor):
    """Extractor for images of a specific genre on 35photo.pro"""
    subcategory = "genre"
    directory_fmt = ("{category}", "Genre", "{genre}")
    archive_fmt = "g{genre_id}_{id}_{num}"
    pattern = r"(?:https?://)?(?:[a-z]+\.)?35photo\.pro/genre_(\d+)(/new/)?"
    test = ("https://35photo.pro/genre_109/",)

    def __init__(self, match):
        _35photoExtractor.__init__(self, match)
        self.genre_id, self.new = match.groups()
        self.photo_ids = None

    def metadata(self):
        url = "{}/genre_{}{}".format(self.root, self.genre_id, self.new or "/")
        page = self.request(url).text
        self.photo_ids = self._photo_ids(text.extract(
            page, ' class="photo', '\n')[0])
        return {
            "genre": text.extract(page, " genre - ", ". ")[0],
            "genre_id": text.parse_int(self.genre_id),
        }

    def photos(self):
        if not self.photo_ids:
            return ()
        return self._pagination({
            "page": "genre",
            "community_id": self.genre_id,
            "photo_rating": "0" if self.new else "50",
            "lastId": self.photo_ids[-1],
        }, self.photo_ids)


class _35photoImageExtractor(_35photoExtractor):
    """Extractor for individual images from 35photo.pro"""
    subcategory = "image"
    pattern = r"(?:https?://)?(?:[a-z]+\.)?35photo\.pro/photo_(\d+)"
    test = ("https://35photo.pro/photo_753340/", {
        "count": 1,
        "keyword": {
            "url"        : r"re:https://m\d+.35photo.pro/photos_main/.*.jpg",
            "id"         : 753340,
            "title"      : "Winter walk",
            "description": str,
            "tags"       : list,
            "views"      : int,
            "favorites"  : int,
            "score"      : int,
            "type"       : 0,
            "date"       : "15 авг, 2014",
            "user"       : "liya",
            "user_id"    : 20415,
            "user_name"  : "Liya Mirzaeva",
        },
    })

    def __init__(self, match):
        _35photoExtractor.__init__(self, match)
        self.photo_id = match.group(1)

    def photos(self):
        return (self.photo_id,)
