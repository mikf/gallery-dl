# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.facebook.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)www\.facebook\.com"


class FacebookExtractor(Extractor):
    """Base class for Facebook extractors"""
    category = "facebook"
    root = "https://www.facebook.com"
    filename_fmt = "{filename}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.match = match

    def _init(self):
        self.session.headers["Accept"] = "text/html"
        self.session.headers["Sec-Fetch-Mode"] = "navigate"

    def item_filename_handle(self, item):
        if "filename" in item or item["filename"] is not None:
            if "." in item["filename"]:
                item["name"], _, item["extension"] = (
                    item["filename"].rpartition(".")
                )
            else:
                item["name"] = item["filename"]
                item["extension"] = ""

    def set_photos_iter(self, set_id):
        PHOTO_PAGE_URL_FORMAT = self.root + "/photo/?fbid={id}&set={set_id}"

        set_page_url = self.root + "/media/set/?set=" + set_id
        set_page = self.request(set_page_url).text

        directory = {
            "set_id": set_id,
            "title": text.parse_unicode_escapes(text.extr(
                set_page,
                '"title":{"text":"',
                '"'
            )),
            "username": text.parse_unicode_escapes(text.extr(
                set_page,
                '{"__typename":"User","name":"',
                '","',
                text.extr(set_page, '"userVanity":"', '","')
            )),
            "user_id": text.extr(
                set_page,
                '"owner":{"__typename":"User","id":"',
                '"'
            )
        }

        # print("\n", directory, "\n")

        yield Message.Directory, directory

        cur_id = text.extr(
            set_page,
            '{"__typename":"Photo","id":"',
            '"',
            text.extr(
                set_page,
                '{"__typename":"Photo","__isMedia":"Photo","',
                '","'
            ).rsplit('"', 1)[1]
        )

        # print("\n", cur_id, "\n")

        all_ids = [cur_id]

        num = 0

        while True:
            num += 1

            media_page_req = self.request(
                PHOTO_PAGE_URL_FORMAT.format(id=cur_id, set_id=set_id)
            )

            if media_page_req.url.startswith(self.root + "/login"):
                raise exception.AuthenticationError()

            media_page = media_page_req.text

            photo = {
                "id": cur_id,
                "set_id": set_id,
                "url": text.extr(
                    media_page,
                    '"},"extensions":{"prefetch_uris_v2":[{"uri":"',
                    '"'
                ).replace("\\/", "/"),
                "num": num
            }

            photo["filename"] = text.rextract(photo["url"], "/", "?")[0]

            # print("\n", photo, "\n")

            self.item_filename_handle(photo)

            yield Message.Url, photo["url"], photo

            next_id = text.extr(
                media_page,
                '"nextMediaAfterNodeId":{"__typename":"Photo","id":"',
                '"',
                text.extr(
                    media_page,
                    ('"nextMedia":{"edges":[{"node":'
                     '{"__typename":"Photo","id":"'),
                    '"'
                )
            )

            # print("\n", next_id, "\n")

            if next_id == "" or next_id in all_ids:
                break
            else:
                cur_id = next_id
                all_ids.append(cur_id)


class FacebookAlbumExtractor(FacebookExtractor):
    """Base class for Facebook Album extractors"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/media/set/.*set=([^/?&]+)"
    directory_fmt = ("{category}", "{title} ({set_id})")
    example = "https://www.facebook.com/media/set/?set=SET_ID"

    def items(self):
        metadata_iter = self.set_photos_iter(self.match.group(1))

        for message in metadata_iter:
            yield message


class FacebookProfileExtractor(FacebookExtractor):
    """Base class for Facebook Profile extractors"""
    subcategory = "profile"
    pattern = BASE_PATTERN + r"/([^/|?]+)"
    directory_fmt = ("{category}", "{title} ({set_id})")
    example = "https://www.facebook.com/ID"

    def items(self):
        photos_page_url = self.root + "/" + self.match.group(1) + "/photos"
        photos_page = text.extract_from(self.request(photos_page_url).text)

        photos_page('{"__typename":"Photo","id":"', '"')
        set_id = photos_page('set=', '"')
        set_id = set_id.rsplit("&", 1)[0]
        # print("\n", set_id, "\n")

        metadata_iter = self.set_photos_iter(set_id)

        for message in metadata_iter:
            yield message
