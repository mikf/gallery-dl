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
    filename_fmt = "{id}.{extension}"
    directory_fmt = ("{category}", "{username}", "{title} ({set_id})")

    set_url_fmt = root + "/media/set/?set={set_id}"
    photo_url_fmt = root + "/photo/?fbid={photo_id}&set={set_id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.match = match

    def _init(self):
        self.session.headers["Accept"] = "text/html"
        self.session.headers["Sec-Fetch-Mode"] = "navigate"

        self.fb_cookies = self.session.cookies.get_dict(domain=".facebook.com")
        if self.fb_cookies:
            self.session.cookies.clear(domain=".facebook.com")

        self.fallback_retries = self.config("fallback-retries", 2)
        self.sleep_429 = self.config("sleep-429", 5)

        self.author_followups = self.config("author-followups", False)

        self.log.warning(
            "Using the Facebook extractor for too long may result in "
            "temporary UI bans of increasing length. "
            "Cookies will only be used when necessary, "
            "and you will be informed if they are. "
            "\nUse at your own risk."
        )

    @staticmethod
    def text_unescape(txt):
        return text.unescape(txt.encode("utf-8").decode("unicode_escape"))

    @staticmethod
    def item_filename_handle(item):
        if "filename" in item and item["filename"] is not None:
            if "." in item["filename"]:
                item["name"], item["extension"] = (
                    item["filename"].rsplit(".", 1)
                )
            else:
                item["name"] = item["filename"]
                item["extension"] = ""
        else:
            item["filename"] = item["name"] = item["extension"] = ""

    @staticmethod
    def get_first_photo_id(set_page):
        photo_id = text.extr(
            set_page,
            '{"__typename":"Photo","__isMedia":"Photo","',
            '","creation_story"'
        ).rsplit('"id":"', 1)[-1]

        if photo_id == "":
            photo_id = text.extr(
                set_page,
                '{"__typename":"Photo","id":"',
                '"'
            )

        return photo_id

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
        photo = {
            "id": text.extr(
                photo_page, '"__isNode":"Photo","id":"', '"'
            ),
            "set_id": text.extr(
                photo_page, 'www.facebook.com\\/photo\\/?fbid=', '"'
            ).rsplit("&set=", 1)[-1],
            "username": text.extr(
                photo_page, '"owner":{"__typename":"User","name":"', '"'
            ),
            "date": text.parse_timestamp(text.extr(
                photo_page, '\\"publish_time\\":', ','
            )),
            "caption": FacebookExtractor.text_unescape(text.extr(
                photo_page,
                '"message":{"delight_ranges"',
                '"},"message_preferred_body"'
            ).rsplit('],"text":"', 1)[-1]),
            "reactions": text.extr(
                photo_page, '"reaction_count":{"count":', ","
            ),
            "comments": text.extr(
                photo_page, '"comments":{"total_count":', "}"
            ),
            "shares": text.extr(
                photo_page, '"share_count":{"count":', ","
            ),
            "url": text.extr(
                photo_page,
                '"},"extensions":{"prefetch_uris_v2":[{"uri":"',
                '"'
            ).replace("\\/", "/"),
        }

        photo["filename"] = text.rextract(photo["url"], "/", "?")[0]
        FacebookExtractor.item_filename_handle(photo)

        return photo

    @staticmethod
    def get_photo_page_author_comments_photo_ids(photo_page):
        comments_raw_iter = text.extract_iter(
            photo_page, '{"node":{"id"', '"cursor":null}'
        )

        photo_ids = []
        for comment_raw in comments_raw_iter:
            if ('"is_author_original_poster":true' in comment_raw and
                    '{"__typename":"Photo","id":"' in comment_raw):
                photo_ids.append(text.extr(
                    comment_raw,
                    '{"__typename":"Photo","id":"',
                    '"'
                ))

        return photo_ids

    @staticmethod
    def get_set_page_metadata(set_page):
        directory = {
            "username": FacebookExtractor.text_unescape(text.extr(
                set_page, '"User","name":"', '","'
            )),
            "user_id": text.extr(
                set_page, '"owner":{"__typename":"User","id":"', '"'
            ),
            "set_id": text.extr(
                set_page, '"mediaSetToken":"', '"',
                text.extr(set_page, '"mediasetToken":"', '"')
            ),
            "title": FacebookExtractor.text_unescape(text.extr(
                set_page, '"title":{"text":"', '"'
            )),
            "description": FacebookExtractor.text_unescape(text.extr(
                set_page, '"message":{"delight_ranges"', '"},'
            ).rsplit('],"text":"', 1)[-1]),
        }

        return directory

    def photo_page_request_wrapper(self, url, *args, **kwargs):
        res = self.request(url, *args, **kwargs)

        if res.url.startswith(self.root + "/login"):
            ERROR_TXT = "You must be logged in to continue viewing images."
            used_cookies = self.session.cookies.get_dict(
                domain=".facebook.com"
            )

            if "datr" in self.fb_cookies and "datr" not in used_cookies:
                self.session.cookies.set(
                    "datr", self.fb_cookies["datr"], domain=".facebook.com"
                )
                res = self.photo_page_request_wrapper(url, *args, **kwargs)
                self.log.debug(ERROR_TXT + " Using session from now on.")
            elif "c_user" in self.fb_cookies and "c_user" not in used_cookies:
                self.session.cookies.set(
                    "c_user", self.fb_cookies["c_user"], domain=".facebook.com"
                )
                self.session.cookies.set(
                    "xs", self.fb_cookies["xs"], domain=".facebook.com"
                )
                res = self.photo_page_request_wrapper(url, *args, **kwargs)
                self.log.info(ERROR_TXT + " Using cookies from now on.")
            else:
                raise exception.AuthenticationError(ERROR_TXT)

        if '{"__dr":"CometErrorRoot.react"}' in res.text:
            raise exception.StopExtraction(
                "You've been temporarily blocked from viewing images. "
                "Please use a different account or try again later."
            )

        return res

    def set_photos_iter(self, set_id):
        set_url = self.set_url_fmt.format(set_id=set_id)
        set_page = self.request(set_url).text

        directory = self.get_set_page_metadata(set_page)

        yield Message.Directory, directory

        all_photo_ids = [self.get_first_photo_id(set_page)]

        retries = 0
        i = 0

        while i < len(all_photo_ids):
            photo_id = all_photo_ids[i]
            photo_url = self.photo_url_fmt.format(
                photo_id=photo_id, set_id=set_id
            )
            media_page = self.photo_page_request_wrapper(photo_url).text

            photo = self.get_photo_page_metadata(media_page)
            photo["num"] = i + 1

            if self.author_followups:
                for comment_photo_id in (
                    self.get_photo_page_author_comments_photo_ids(media_page)
                ):
                    if comment_photo_id not in all_photo_ids:
                        self.log.debug(
                            "Found a followup in comments:" + comment_photo_id
                        )
                        all_photo_ids.append(comment_photo_id)

            if photo["url"] == "":
                if retries < self.fallback_retries:
                    self.log.debug(
                        "Failed to find photo download URL for " + photo_url +
                        ". Retrying in " + self.sleep_429 + " seconds."
                    )
                    self.sleep(self.sleep_429, "retry")
                    retries += 1
                    continue
                else:
                    self.log.warning(
                        "Failed to find photo download URL for " + photo_url +
                        ". Skipping."
                    )
                    retries = 0
            else:
                retries = 0
                yield Message.Url, photo["url"], photo

            next_photo_id = self.get_next_photo_id(media_page)

            if next_photo_id == "":
                self.log.debug(
                    "Can't find next image in the set. "
                    "Extraction is over."
                )
            elif next_photo_id in all_photo_ids:
                if next_photo_id != photo_id:
                    self.log.debug(
                        "Detected a loop in the set, it's likely finished. "
                        "Extraction is over."
                    )
            else:
                all_photo_ids.append(next_photo_id)

            i += 1


class FacebookSetExtractor(FacebookExtractor):
    """Base class for Facebook Set extractors"""
    subcategory = "set"
    pattern = BASE_PATTERN + r"/media/set/.*set=([^/?&]+)"
    example = "https://www.facebook.com/media/set/?set=SET_ID"

    def items(self):
        metadata_iter = self.set_photos_iter(self.match.group(1))

        for message in metadata_iter:
            yield message


class FacebookPhotoExtractor(FacebookExtractor):
    """Base class for Facebook Photo extractors"""
    subcategory = "photo"
    pattern = BASE_PATTERN + r"/photo.*fbid=([^/?&]+)"
    example = "https://www.facebook.com/photo/?fbid=PHOTO_ID"

    def items(self):
        photo_url = self.photo_url_fmt.format(
            photo_id=self.match.group(1), set_id=""
        )
        photo_page = self.photo_page_request_wrapper(photo_url).text

        i = 1
        photo = self.get_photo_page_metadata(photo_page)
        photo["num"] = i

        set_page = self.request(self.set_url_fmt.format(
            set_id=photo["set_id"]
        )).text

        directory = self.get_set_page_metadata(set_page)

        yield Message.Directory, directory
        yield Message.Url, photo["url"], photo

        if self.author_followups:
            for comment_photo_id in (
                self.get_photo_page_author_comments_photo_ids(photo_page)
            ):
                comment_photo = self.get_photo_page_metadata(
                    self.request(self.photo_url_fmt.format(
                        photo_id=comment_photo_id, set_id=""
                    )).text
                )
                i += 1
                comment_photo["num"] = i
                yield Message.Url, comment_photo["url"], comment_photo


class FacebookProfileExtractor(FacebookExtractor):
    """Base class for Facebook Profile Photos Set extractors"""
    subcategory = "profile"
    pattern = BASE_PATTERN + r"/([^/|?]+)"
    example = "https://www.facebook.com/USERNAME"

    @staticmethod
    def get_profile_photos_set_id(profile_photos_page):
        profile_photos_page_extr = text.extract_from(profile_photos_page)
        profile_photos_page_extr('"pageItems"', '"actions_renderer"')
        set_id = profile_photos_page_extr('set=', '"').rsplit("&", 1)[0]
        return set_id

    def items(self):
        profile_photos_url = (
            self.root + "/" + self.match.group(1) + "/photos_by"
        )
        profile_photos_page = self.request(profile_photos_url).text

        if '"comet.profile.collection.photos_by"' not in profile_photos_page:
            return

        set_id = self.get_profile_photos_set_id(profile_photos_page)

        metadata_iter = self.set_photos_iter(set_id)

        for message in metadata_iter:
            yield message
