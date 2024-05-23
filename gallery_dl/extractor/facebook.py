# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.facebook.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?facebook\.com"


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

    @staticmethod
    def raise_request_exceptions(res):
        if res.url.startswith(FacebookExtractor.root + "/login"):
            raise exception.AuthenticationError()
        if '{"__dr":"CometErrorRoot.react"}' in res.text:
            raise exception.StopExtraction(
                "You've been temporarily blocked from viewing images. "
                "Please try again later."
            )
        return res

    @staticmethod
    def item_filename_handle(item):
        if "filename" in item and item["filename"] is not None:
            if "." in item["filename"]:
                item["name"], _, item["extension"] = (
                    item["filename"].rpartition(".")
                )
            else:
                item["name"] = item["filename"]
                item["extension"] = ""
        else:
            item["filename"] = item["name"] = item["extension"] = ""

    @staticmethod
    def get_first_photo_id(album_page):
        return text.extr(
            album_page,
            '{"__typename":"Photo","id":"',
            '"',
            text.extr(
                album_page,
                '{"__typename":"Photo","__isMedia":"Photo","',
                '","'
            ).rsplit('"', 1)[-1]
        )

    @staticmethod
    def get_next_photo_id(photo_page):
        return text.extr(
            photo_page,
            '"nextMediaAfterNodeId":{"__typename":"Photo","id":"',
            '"',
            text.extr(
                photo_page,
                '"nextMedia":{"edges":[{"node":{"__typename":"Photo","id":"',
                '"'
            )
        )

    @staticmethod
    def get_photo_download_url(photo_page):
        return text.extr(
            photo_page,
            '"},"extensions":{"prefetch_uris_v2":[{"uri":"',
            '"'
        ).replace("\\/", "/")

    def album_photos_iter(self, set_id):
        PHOTO_URL = self.root + "/photo/?fbid={photo_id}&set={set_id}"

        album_url = self.root + "/media/set/?set=" + set_id
        album_page = self.request(album_url).text

        directory = {
            "set_id": set_id,
            "title": text.parse_unicode_escapes(text.extr(
                album_page,
                '"title":{"text":"',
                '"'
            )),
            "username": text.parse_unicode_escapes(text.extr(
                album_page,
                '"User","name":"',
                '","'
            )),
            "user_id": text.extr(
                album_page,
                '"owner":{"__typename":"User","id":"',
                '"'
            )
        }

        # print("\n", directory, "\n")

        yield Message.Directory, directory

        cur_photo_id = self.get_first_photo_id(album_page)

        # print("\n", cur_photo_id, "\n")

        all_photo_ids = [cur_photo_id]

        num = 0

        while True:
            num += 1

            media_page = self.raise_request_exceptions(self.request(
                PHOTO_URL.format(photo_id=cur_photo_id, set_id=set_id)
            )).text

            photo = {
                "id": cur_photo_id,
                "set_id": set_id,
                "url": self.get_photo_download_url(media_page),
                "num": num
            }

            photo["filename"] = text.rextract(photo["url"], "/", "?")[0]

            # print("\n", photo, "\n")

            self.item_filename_handle(photo)

            yield Message.Url, photo["url"], photo

            next_photo_id = self.get_next_photo_id(media_page)

            # print("\n", next_photo_id, "\n")

            if next_photo_id == "" or next_photo_id in all_photo_ids:
                break
            else:
                cur_photo_id = next_photo_id
                all_photo_ids.append(cur_photo_id)


class FacebookAlbumExtractor(FacebookExtractor):
    """Base class for Facebook Album extractors"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/media/set/.*set=([^/?&]+)"
    directory_fmt = ("{category}", "{title} ({set_id})")
    example = "https://www.facebook.com/media/set/?set=SET_ID"

    def items(self):
        metadata_iter = self.album_photos_iter(self.match.group(1))

        for message in metadata_iter:
            yield message


class FacebookProfileExtractor(FacebookExtractor):
    """Base class for Facebook Profile extractors"""
    subcategory = "profile"
    pattern = BASE_PATTERN + r"/([^/|?]+)"
    directory_fmt = ("{category}", "{title} ({set_id})")
    example = "https://www.facebook.com/ID"

    @staticmethod
    def get_profile_photos_album_id(profile_photos_page):
        profile_photos_page_extr = text.extract_from(profile_photos_page)
        profile_photos_page_extr('"pageItems"', '"actions_renderer"')
        set_id = profile_photos_page_extr('set=', '"').rsplit("&", 1)[0]
        return set_id

    def items(self):
        profile_photos_url = f"{self.root}/{self.match.group(1)}/photos_by"
        profile_photos_page = self.request(profile_photos_url).text

        set_id = self.get_profile_photos_album_id(profile_photos_page)
        # print("\n", set_id, "\n")

        metadata_iter = self.album_photos_iter(set_id)

        for message in metadata_iter:
            yield message
