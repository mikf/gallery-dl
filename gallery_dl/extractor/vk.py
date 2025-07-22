# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vk.com/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https://)?(?:www\.|m\.)?vk\.com"


class VkExtractor(Extractor):
    """Base class for vk extractors"""
    category = "vk"
    directory_fmt = ("{category}", "{user[name]|user[id]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://vk.com"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.offset = text.parse_int(self.config("offset"))

    def finalize(self):
        if self.offset:
            self.log.info("Use '-o offset=%s' to continue downloading "
                          "from the current position", self.offset)

    def skip(self, num):
        self.offset += num
        return num

    def items(self):
        subn = util.re(r"/imp[fg]/").subn
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
                url = photo[size + "src"]
            except KeyError:
                self.log.warning("no photo URL found (%s)", photo.get("id"))
                continue

            url_sub, count = subn("/", url.partition("?")[0])
            if count:
                photo["_fallback"] = (url,)
                photo["url"] = url = url_sub
            else:
                photo["url"] = url

            try:
                _, photo["width"], photo["height"] = photo[size]
            except ValueError:
                # photo without width/height entries (#2535)
                photo["width"] = photo["height"] = 0

            photo["id"] = photo["id"].rpartition("_")[2]
            photo.update(data)

            text.nameext_from_url(url, photo)
            yield Message.Url, url, photo

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
            "offset"   : self.offset,
        }

        while True:
            response = self.request(
                url, method="POST", headers=headers, data=data)
            if response.history and "/challenge.html" in response.url:
                raise exception.AbortExtraction(
                    f"HTTP redirect to 'challenge' page:\n{response.url}")

            payload = response.json()["payload"][1]
            if len(payload) < 4:
                self.log.debug(payload)
                raise exception.AuthorizationError(
                    text.unescape(payload[0]) if payload[0] else None)

            total = payload[1]
            photos = payload[3]

            offset_next = self.offset + len(photos)
            if offset_next >= total:
                # the last chunk of photos also contains the first few photos
                # again if 'total' is not a multiple of 10
                if extra := total - offset_next:
                    del photos[extra:]

                yield from photos
                self.offset = 0
                return

            yield from photos
            data["offset"] = self.offset = offset_next


class VkPhotosExtractor(VkExtractor):
    """Extractor for photos from a vk user"""
    subcategory = "photos"
    pattern = (BASE_PATTERN + r"/(?:"
               r"(?:albums|photos|id)(-?\d+)"
               r"|(?!(?:album|tag)-?\d+_?)([^/?#]+))")
    example = "https://vk.com/id12345"

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id, self.user_name = match.groups()

    def photos(self):
        return self._pagination("photos" + self.user_id)

    def metadata(self):
        if self.user_id:
            user_id = self.user_id
            prefix = "public" if user_id[0] == "-" else "id"
            url = f"{self.root}/{prefix}{user_id.lstrip('-')}"
            data = self._extract_profile(url)
        else:
            url = f"{self.root}/{self.user_name}"
            data = self._extract_profile(url)
            self.user_id = data["user"]["id"]
        return data

    def _extract_profile(self, url):
        page = self.request(url).text
        extr = text.extract_from(page)

        user = {
            "id"  : extr('property="og:url" content="https://vk.com/id', '"'),
            "nick": text.unescape(extr(
                "<title>", " | VK</title>")),
            "info": text.unescape(extr(
                ',"activity":"', '","')).replace("\\/", "/"),
            "name": extr('href="https://m.vk.com/', '"'),
        }

        if user["id"]:
            user["group"] = False
        else:
            user["group"] = True
            user["id"] = extr('data-from-id="', '"')

        return {"user": user}


class VkAlbumExtractor(VkExtractor):
    """Extractor for a vk album"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user[id]}", "{album[id]}")
    pattern = BASE_PATTERN + r"/album(-?\d+)_(\d+)$"
    example = "https://vk.com/album12345_00"

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id, self.album_id = match.groups()

    def photos(self):
        return self._pagination(f"album{self.user_id}_{self.album_id}")

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
    example = "https://vk.com/tag12345"

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id = match[1]

    def photos(self):
        return self._pagination(f"tag{self.user_id}")

    def metadata(self):
        return {"user": {"id": self.user_id}}
