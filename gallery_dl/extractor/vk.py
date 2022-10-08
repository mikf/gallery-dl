# -*- coding: utf-8 -*-

# Copyright 2021-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vk.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https://)?(?:www\.|m\.)?vk\.com"


class VkExtractor(Extractor):
    """Base class for vk extractors"""
    category = "vk"
    directory_fmt = ("{category}", "{user[name]|user[id]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://vk.com"
    request_interval = 1.0

    def items(self):
        sizes = "wzyxrqpo"

        data = self.metadata()
        yield Message.Directory, data

        for photo in self.photos():

            for size in sizes:
                size += "_"
                if size in photo:
                    break
            else:
                self.log.warning("no photo URL found (%s)", photo.get("id"))
                continue

            try:
                photo["url"] = photo[size + "src"]
            except KeyError:
                self.log.warning("no photo URL found (%s)", photo.get("id"))
                continue

            try:
                _, photo["width"], photo["height"] = photo[size]
            except ValueError:
                # photo without width/height entries (#2535)
                photo["width"] = photo["height"] = 0

            photo["id"] = photo["id"].rpartition("_")[2]
            photo.update(data)

            text.nameext_from_url(photo["url"], photo)
            yield Message.Url, photo["url"], photo

    def _pagination(self, photos_id):
        url = self.root + "/al_photos.php"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Origin"          : self.root,
            "Referer"         : self.root + "/" + photos_id,
        }
        data = {
            "act"      : "show",
            "al"       : "1",
            "direction": "1",
            "list"     : photos_id,
            "offset"   : 0,
        }

        while True:
            payload = self.request(
                url, method="POST", headers=headers, data=data,
            ).json()["payload"][1]

            if len(payload) < 4:
                self.log.debug(payload)
                raise exception.AuthorizationError(
                    text.unescape(payload[0]) if payload[0] else None)

            total = payload[1]
            photos = payload[3]

            data["offset"] += len(photos)
            if data["offset"] >= total:
                # the last chunk of photos also contains the first few photos
                # again if 'total' is not a multiple of 10
                extra = total - data["offset"]
                if extra:
                    del photos[extra:]

                yield from photos
                return

            yield from photos


class VkPhotosExtractor(VkExtractor):
    """Extractor for photos from a vk user"""
    subcategory = "photos"
    pattern = (BASE_PATTERN + r"/(?:"
               r"(?:albums|photos|id)(-?\d+)"
               r"|(?!(?:album|tag)-?\d+_?)([^/?#]+))")
    test = (
        ("https://vk.com/id398982326", {
            "pattern": r"https://sun\d+-\d+\.userapi\.com/s/v1/if1"
                       r"/[\w-]+\.jpg\?size=\d+x\d+&quality=96&type=album",
            "count": ">= 35",
            "keywords": {
                "id": r"re:\d+",
                "user": {
                    "id": "398982326",
                    "info": "Мы за Движуху! – m1ni SounD #4 [EROmusic]",
                    "name": "",
                    "nick": "Dobrov Kurva",
                },
            },
        }),
        ("https://vk.com/cosplayinrussia", {
            "range": "15-25",
            "keywords": {
                "id": r"re:\d+",
                "user": {
                    "id"  : "-165740836",
                    "info": "Предложка открыта, кидайте ваши косплейчики. При "
                            "правильном оформлении они будут опубликованы",
                    "name": "cosplayinrussia",
                    "nick": "Косплей | Cosplay 18+",
                },
            },
        }),
        # photos without width/height (#2535)
        ("https://vk.com/id76957806", {
            "pattern": r"https://sun\d+-\d+\.userapi\.com/",
            "range": "1-9",
            "count": 9,
        }),
        ("https://m.vk.com/albums398982326"),
        ("https://www.vk.com/id398982326?profile=1"),
        ("https://vk.com/albums-165740836"),
    )

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id, self.user_name = match.groups()

    def photos(self):
        return self._pagination("photos" + self.user_id)

    def metadata(self):
        if self.user_id:
            user_id = self.user_id
            prefix = "public" if user_id[0] == "-" else "id"
            url = "{}/{}{}".format(self.root, prefix, user_id.lstrip("-"))
            data = self._extract_profile(url)
        else:
            url = "{}/{}".format(self.root, self.user_name)
            data = self._extract_profile(url)
            self.user_id = data["user"]["id"]
        return data

    def _extract_profile(self, url):
        extr = text.extract_from(self.request(url).text)
        return {"user": {
            "name": text.unescape(extr(
                'rel="canonical" href="https://vk.com/', '"')),
            "nick": text.unescape(extr(
                '<h1 class="page_name">', "<")).replace("  ", " "),
            "info": text.unescape(text.remove_html(extr(
                '<span class="current_text">', '</span'))),
            "id"  : (extr('<a href="/albums', '"') or
                     extr('data-from-id="', '"')),
        }}


class VkAlbumExtractor(VkExtractor):
    """Extractor for a vk album"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user[id]}", "{album[id]}")
    pattern = BASE_PATTERN + r"/album(-?\d+)_(\d+)$"
    test = (
        ("https://vk.com/album-165740836_281339889", {
            "count": 12,
        }),
        # "Access denied" (#2556)
        ("https://vk.com/album-53775183_00", {
            "exception": exception.AuthorizationError,
        }),
        ("https://vk.com/album232175027_00", {
            "exception": exception.AuthorizationError,
        }),
    )

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id, self.album_id = match.groups()

    def photos(self):
        return self._pagination("album{}_{}".format(
            self.user_id, self.album_id))

    def metadata(self):
        return {
            "user": {"id": self.user_id},
            "album": {"id": self.album_id},
        }


class VkTaggedExtractor(VkExtractor):
    """Extractor for a vk tagged photos"""
    subcategory = "tagged"
    directory_fmt = ("{category}", "{user[id]}", "tags")
    pattern = BASE_PATTERN + r"/tag(-?\d+)$"
    test = (
        ("https://vk.com/tag304303884", {
            "count": 44,
        }),
    )

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id = match.group(1)

    def photos(self):
        return self._pagination("tag{}".format(self.user_id))

    def metadata(self):
        return {"user": {"id": self.user_id}}
