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
        self.fallback_retries = self.config("fallback-retries", 2)
        self.sleep_429 = self.config("sleep-429", 5)
        self.log.warning(
            "Using the Facebook extractor for too long may result in "
            "temporary UI bans of increasing length. Use at your own risk."
        )

    @staticmethod
    def raise_request(res):
        if res.url.startswith(FacebookExtractor.root + "/login"):
            raise exception.AuthenticationError(
                "You need to be logged in to view this content."
            )
        if '{"__dr":"CometErrorRoot.react"}' in res.text:
            raise exception.StopExtraction(
                "You've been temporarily blocked from viewing this image. "
                "Please try again later or use a different account."
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
    def get_photo_page_metadata(photo_page):
        # TODO: add date, author, id, set id ecc.
        photo = {}

        photo["url"] = text.extr(
            photo_page,
            '"},"extensions":{"prefetch_uris_v2":[{"uri":"',
            '"'
        ).replace("\\/", "/")

        photo["filename"] = text.rextract(photo["url"], "/", "?")[0]
        FacebookExtractor.item_filename_handle(photo)

        return photo

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

        all_photo_ids = set([cur_photo_id])

        num = 0
        retries = 0

        while True:
            num += 1

            photo_url = PHOTO_URL.format(photo_id=cur_photo_id, set_id=set_id)
            media_page = self.raise_request(self.request(photo_url)).text

            photo = self.get_photo_page_metadata(media_page)
            photo["id"] = cur_photo_id
            photo["set_id"] = set_id
            photo["num"] = num

            # print("\n", photo, "\n")

            if photo["url"] == "":
                if retries < self.fallback_retries:
                    # TODO: change to log.debug
                    self.log.warning(
                        f"Failed to find photo download URL for {photo_url}. "
                        f"Retrying in {self.sleep_429} seconds."
                    )
                    self.sleep(self.sleep_429, "retry")
                    retries += 1
                    num -= 1
                    continue
                else:
                    self.log.warning(
                        f"Failed to find photo download URL for {photo_url}. "
                        "Skipping."
                    )
                    retries = 0
            else:
                yield Message.Url, photo["url"], photo

            next_photo_id = self.get_next_photo_id(media_page)

            # print("\n", next_photo_id, "\n")

            if next_photo_id == "":
                # TODO: change to log.debug
                self.log.warning(
                    "Can't find next image in the set. Quitting."
                )
                break
            elif next_photo_id in all_photo_ids:
                # TODO: change to log.debug
                self.log.warning(
                    "Detected a loop in the set, it's likely over. Quitting."
                )
                break
            else:
                cur_photo_id = next_photo_id
                all_photo_ids.add(cur_photo_id)


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


class FacebookPhotoExtractor(FacebookExtractor):
    """Base class for Facebook Photo extractors"""
    subcategory = "photo"
    pattern = BASE_PATTERN + r"/photo.*fbid=([^/?&]+)"
    directory_fmt = ("{category}", "{subcategory}")
    example = "https://www.facebook.com/photo/?fbid=PHOTO_ID"

    def items(self):
        photo_url = f"{self.root}/photo/?fbid={self.match.group(1)}"
        photo_page = self.request(photo_url).text

        photo = self.get_photo_page_metadata(photo_page)
        photo["id"] = self.match.group(1)
        photo["num"] = 1

        # print("\n", photo, "\n")

        yield Message.Directory, {}
        yield Message.Url, photo["url"], photo


class FacebookProfileExtractor(FacebookExtractor):
    """Base class for Facebook Profile Photos Album extractors"""
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

        if '"comet.profile.collection.photos_by"' not in profile_photos_page:
            return

        set_id = self.get_profile_photos_album_id(profile_photos_page)
        # print("\n", set_id, "\n")

        metadata_iter = self.album_photos_iter(set_id)

        for message in metadata_iter:
            yield message
