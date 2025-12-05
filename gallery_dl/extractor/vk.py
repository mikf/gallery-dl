# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
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
    archive_fmt = "{user[id]}_{id}"
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
        subn = text.re(r"/imp[fg]/").subn
        sizes = "wzyxrqpo"

        data = self.metadata()
        yield Message.Directory, "", data

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
            photo["date"] = self.parse_timestamp(text.extr(
                photo["date"], 'data-date="', '"'))
            photo["description"] = text.unescape(text.extr(
                photo.get("desc", ""), ">", "<"))
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

            for i in range(len(photos)):
                photos[i]["num"] = self.offset + i + 1
                photos[i]["count"] = total

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
    pattern = (rf"{BASE_PATTERN}/(?:"
               r"(?:albums|photos|id)(-?\d+)"
               r"|(?!(?:album|tag|wall)-?\d+_?)([^/?#]+))")
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
    pattern = rf"{BASE_PATTERN}/album(-?\d+)_(\d+)$"
    example = "https://vk.com/album12345_00"

    def photos(self):
        user_id, album_id = self.groups
        return self._pagination(f"album{user_id}_{album_id}")

    def metadata(self):
        user_id, album_id = self.groups

        url = f"{self.root}/album{user_id}_{album_id}"
        page = self.request(url).text
        desc = text.extr(page, 'name="og:description" value="', '"')
        try:
            album_name, user_name, photos = desc.rsplit(" - ", 2)
        except ValueError:
            if msg := text.extr(
                    page, '<div class="message_page_title">Error</div>',
                    "</div>"):
                msg = f" ('{text.remove_html(msg)[:-5]}')"
            self.log.warning("%s_%s: Failed to extract metadata%s",
                             user_id, album_id, msg)
            return {"user": {"id": user_id}, "album": {"id": album_id}}

        return {
            "user": {
                "id"   : user_id,
                "nick" : text.unescape(user_name),
                "name" : text.unescape(text.extr(
                    page, 'class="ui_crumb" href="/', '"')),
                "group": user_id[0] == "-",
            },
            "album": {
                "id"   : album_id,
                "name" : text.unescape(album_name),
                "count": text.parse_int(photos[:-7])
            },
        }


class VkTaggedExtractor(VkExtractor):
    """Extractor for a vk tagged photos"""
    subcategory = "tagged"
    directory_fmt = ("{category}", "{user[id]}", "tags")
    pattern = rf"{BASE_PATTERN}/tag(-?\d+)$"
    example = "https://vk.com/tag12345"

    def __init__(self, match):
        VkExtractor.__init__(self, match)
        self.user_id = match[1]

    def photos(self):
        return self._pagination(f"tag{self.user_id}")

    def metadata(self):
        return {"user": {"id": self.user_id}}


class VkWallPostExtractor(VkExtractor):
    """Extractor for a vk wall post"""
    subcategory = "wall-post"
    directory_fmt = ("{category}", "{user[id]}", "wall")
    filename_fmt = "{wall[id]}_{num}.{extension}"
    pattern = rf"{BASE_PATTERN}/wall(-?\d+)_(\d+)"
    example = "https://vk.com/wall12345_123"

    def photos(self):
        user_id, wall_id = self.groups
        return self._pagination(f"wall{user_id}_{wall_id}")

    def metadata(self):
        user_id, wall_id = self.groups

        url = f"{self.root}/wall{user_id}_{wall_id}"
        page = self.request(url).text
        desc = text.unescape(
            text.extr(page, 'data-testid="post_description">', "</div>") or
            text.extr(page, 'name="description" content="', '"'))

        return {
            "user": {
                "id": user_id,
            },
            "wall": {
                "id": wall_id,
                "description": desc,
            },
        }
