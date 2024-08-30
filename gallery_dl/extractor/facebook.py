# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.facebook.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?.*?facebook\.com"


class FacebookExtractor(Extractor):
    """Base class for Facebook extractors"""
    category = "facebook"
    root = "https://www.facebook.com"
    directory_fmt = ("{category}", "{username}", "{title} ({set_id})")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}.{extension}"

    set_url_fmt = root + "/media/set/?set={set_id}"
    photo_url_fmt = root + "/photo/?fbid={photo_id}&set={set_id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.match = match

    def _init(self):
        self.session.headers["Accept"] = "text/html"
        self.session.headers["Sec-Fetch-Mode"] = "navigate"

        self.fallback_retries = self.config("fallback-retries", 2)
        self.sleep_429 = self.config("sleep-429", 5)
        self.videos = self.config("videos", True)

        self.author_followups = self.config("author-followups", False)

    @staticmethod
    def decode_all(txt):
        return text.unescape(
            txt.encode("utf-8").decode("unicode_escape")
        ).replace("\\/", "/")

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
    def get_set_page_metadata(set_page):
        directory = {
            "username": FacebookExtractor.decode_all(text.extr(
                set_page, '"user":{"__isProfile":"User","name":"', '","',
                text.extr(
                    set_page, '"actors":[{"__typename":"User","name":"', '","'
                )
            )),
            "user_id": text.extr(
                set_page, '"owner":{"__typename":"User","id":"', '"'
            ),
            "set_id": text.extr(
                set_page, '"mediaSetToken":"', '"',
                text.extr(set_page, '"mediasetToken":"', '"')
            ),
            "title": FacebookExtractor.decode_all(text.extr(
                set_page, '"title":{"text":"', '"'
            )),
            "description": FacebookExtractor.decode_all(text.extr(
                set_page, '"message":{"delight_ranges"', '"},"group_album'
            ).rsplit('],"text":"', 1)[-1]),
            "first_photo_id": text.extr(
                set_page,
                '{"__typename":"Photo","__isMedia":"Photo","',
                '","creation_story"'
            ).rsplit('"id":"', 1)[-1]
        }

        if directory["first_photo_id"] == "":
            directory["first_photo_id"] = text.extr(
                set_page, '{"__typename":"Photo","id":"', '"'
            )

        return directory

    @staticmethod
    def get_photo_page_metadata(photo_page):
        photo = {
            "id": text.extr(
                photo_page, '"__isNode":"Photo","id":"', '"'
            ),
            "set_id": text.extr(
                photo_page,
                '"url":"https:\\/\\/www.facebook.com\\/photo\\/?fbid=',
                '"'
            ).rsplit("&set=", 1)[-1],
            "username": FacebookExtractor.decode_all(text.extr(
                photo_page, '"owner":{"__typename":"User","name":"', '"'
            )),
            "date": text.parse_timestamp(text.extr(
                photo_page, '\\"publish_time\\":', ','
            )),
            "caption": FacebookExtractor.decode_all(text.extr(
                photo_page,
                '"message":{"delight_ranges"',
                '"},"message_preferred_body"'
            ).rsplit('],"text":"', 1)[-1]),
            "reactions": int(text.extr(
                photo_page, '"reaction_count":{"count":', ","
            )),
            "comments": int(text.extr(
                photo_page, '{"comments":{"total_count":', "}"
            )),
            "shares": int(text.extr(
                photo_page, '"share_count":{"count":', ","
            )),
            "url": FacebookExtractor.decode_all(text.extr(
                photo_page,
                '"},"extensions":{"prefetch_uris_v2":[{"uri":"',
                '"'
            )),
            "next_photo_id": text.extr(
                photo_page,
                '"nextMediaAfterNodeId":{"__typename":"Photo","id":"',
                '"',
                text.extr(
                    photo_page,  # "n
                    'extMedia":{"edges":[{"node":{"__typename":"Photo","id":"',
                    '"'
                )
            )
        }

        photo["filename"] = text.rextract(photo["url"], "/", "?")[0]
        FacebookExtractor.item_filename_handle(photo)

        photo["followups_ids"] = []
        for comment_raw in text.extract_iter(
            photo_page, '{"node":{"id"', '"cursor":null}'
        ):
            if ('"is_author_original_poster":true' in comment_raw and
                    '{"__typename":"Photo","id":"' in comment_raw):
                photo["followups_ids"].append(text.extr(
                    comment_raw,
                    '{"__typename":"Photo","id":"',
                    '"'
                ))

        return photo

    @staticmethod
    def get_video_page_metadata(video_page):
        video = {
            "id": text.extr(
                video_page, '\\"video_id\\":\\"', '\\"'
            ),
            "username": FacebookExtractor.decode_all(text.extr(
                video_page, '"actors":[{"__typename":"User","name":"', '"'
            )),
            "date": text.parse_timestamp(text.extr(
                video_page, '\\"publish_time\\":', ','
            )),
            "title": FacebookExtractor.decode_all(text.extr(
                video_page, '"},"message":{"text":"', '","delight_ranges"'
            )),
            "reactions": int(text.extr(
                video_page, '}},"i18n_reaction_count":"', '"'
            )),
            "comments": int(text.extr(
                video_page, '{"comments":{"total_count":', '}'
            )),
            "views": int(text.extr(
                video_page, '"video_view_count":', ','
            )),
            "type": "video"
        }

        first_video_del = '{"__dr":"VideoPlayerScrubberDefaultPreview.react"}'
        first_video_raw = text.extr(
            video_page, first_video_del, first_video_del
        )

        audio = {
            **video,
            "url": FacebookExtractor.decode_all(text.extr(
                text.extr(
                    first_video_raw,
                    "AudioChannelConfiguration",
                    "BaseURL>\\u003C"
                ),
                "BaseURL>", "\\u003C\\/"
            )),
            "type": "audio"
        }

        video["urls"] = {}
        for raw_url in text.extract_iter(
            first_video_raw, 'FBQualityLabel=\\"', '\\u003C\\/BaseURL>'
        ):
            resolution = raw_url.split('\\"', 1)[0]
            dl_url = FacebookExtractor.decode_all(
                raw_url.split('BaseURL>', 1)[1]
            )
            video["urls"][resolution] = dl_url
        video["url"] = dl_url

        video["filename"] = text.rextract(video["url"], "/", "?")[0]
        FacebookExtractor.item_filename_handle(video)

        audio["filename"] = video["name"] + ".m4a"
        FacebookExtractor.item_filename_handle(audio)

        return video, audio

    def photo_page_request_wrapper(self, url, *args, **kwargs):
        LEFT_OFF_TXT = "" if url.endswith("&set=") else (
            "\nYou can use this URL to continue from "
            "where you left off (added \"&setextract\"): "
            "\n" + url + "&setextract"
        )

        res = self.request(url, *args, **kwargs)

        if res.url.startswith(self.root + "/login"):
            raise exception.AuthenticationError(
                "You must be logged in to continue viewing images." +
                LEFT_OFF_TXT
            )

        if '{"__dr":"CometErrorRoot.react"}' in res.text:
            raise exception.StopExtraction(
                "You've been temporarily blocked from viewing images. "
                "\nPlease use a different account or try again later." +
                LEFT_OFF_TXT
            )

        return res

    def set_photos_iter(self, first_photo_id, set_id):
        all_photo_ids = [first_photo_id]

        retries = 0
        i = 0

        while i < len(all_photo_ids):
            photo_id = all_photo_ids[i]
            photo_url = self.photo_url_fmt.format(
                photo_id=photo_id, set_id=set_id
            )
            photo_page = self.photo_page_request_wrapper(photo_url).text

            photo = self.get_photo_page_metadata(photo_page)
            photo["num"] = i + 1

            if self.author_followups:
                for followup_id in photo["followups_ids"]:
                    if followup_id not in all_photo_ids:
                        self.log.debug(
                            "Found a followup in comments:" + followup_id
                        )
                        all_photo_ids.append(followup_id)

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
                yield photo

            if photo["next_photo_id"] == "":
                self.log.debug(
                    "Can't find next image in the set. "
                    "Extraction is over."
                )
            elif photo["next_photo_id"] in all_photo_ids:
                if photo["next_photo_id"] != photo["id"]:
                    self.log.debug(
                        "Detected a loop in the set, it's likely finished. "
                        "Extraction is over."
                    )
            else:
                all_photo_ids.append(photo["next_photo_id"])

            i += 1


class FacebookSetExtractor(FacebookExtractor):
    """Base class for Facebook Set extractors"""
    subcategory = "set"
    pattern = (
        BASE_PATTERN + r"(?:/media/set/.*set=([^/?&]+)"
        r"|/photo.*fbid=([^/?&]+).*?(?:set=([^/?&]+))?&setextract)"
    )
    example = "https://www.facebook.com/media/set/?set=SET_ID"

    def items(self):
        set_id = self.match.group(1) or self.match.group(3)
        set_url = self.set_url_fmt.format(set_id=set_id)
        set_page = self.request(set_url).text

        directory = self.get_set_page_metadata(set_page)

        yield Message.Directory, directory

        for photo in self.set_photos_iter(
            (self.match.group(2) or directory["first_photo_id"]),
            directory["set_id"]
        ):
            yield Message.Url, photo["url"], photo


class FacebookPhotoExtractor(FacebookExtractor):
    """Base class for Facebook Photo extractors"""
    subcategory = "photo"
    pattern = BASE_PATTERN + r"/(?:.*/photos.*/|photo.*fbid=)([^/?&]+)"
    example = "https://www.facebook.com/photo/?fbid=PHOTO_ID"

    def items(self):
        photo_url = self.photo_url_fmt.format(
            photo_id=self.match.group(1), set_id=""
        )
        photo_page = self.photo_page_request_wrapper(photo_url).text

        i = 1
        photo = self.get_photo_page_metadata(photo_page)
        photo["num"] = i

        set_page = self.request(
            self.set_url_fmt.format(set_id=photo["set_id"])
        ).text

        directory = self.get_set_page_metadata(set_page)

        yield Message.Directory, directory
        yield Message.Url, photo["url"], photo

        if self.author_followups:
            for comment_photo_id in photo["followups_ids"]:
                comment_photo = self.get_photo_page_metadata(
                    self.photo_page_request_wrapper(
                        self.photo_url_fmt.format(
                            photo_id=comment_photo_id, set_id=""
                        )
                    ).text
                )
                i += 1
                comment_photo["num"] = i
                yield Message.Url, comment_photo["url"], comment_photo


class FacebookVideoExtractor(FacebookExtractor):
    """Base class for Facebook Video extractors"""
    subcategory = "video"
    pattern = BASE_PATTERN + r"/(?:.+/videos/|watch/.*\?v=)([^/]+)"
    example = "https://www.facebook.com/watch/?v=VIDEO_ID"
    directory_fmt = ("{category}", "{username}", "{subcategory}")

    def items(self):
        video_id = self.match.group(1)
        video_url = self.root + "/watch/?v=" + video_id
        video_page = self.request(video_url).text

        video, audio = self.get_video_page_metadata(video_page)

        yield Message.Directory, video

        if self.videos == "ytdl":
            yield Message.Url, "ytdl:" + video_url, video
        else:
            yield Message.Url, video["url"], video
            if audio["url"]:
                yield Message.Url, audio["url"], audio


class FacebookProfileExtractor(FacebookExtractor):
    """Base class for Facebook Profile Photos Set extractors"""
    subcategory = "profile"
    pattern = (
        BASE_PATTERN + r"/(?!(?:media|photo|watch)/)"
        r"(?:profile.php\?id=|people/[^/|?|&]+/)?([^/|?|&]+)"
    )
    example = "https://www.facebook.com/USERNAME"

    @staticmethod
    def get_profile_photos_set_id(profile_photos_page):
        set_ids_raw = text.extr(
            profile_photos_page, '"pageItems"', '"page_info"'
        )
        set_id = text.extr(set_ids_raw, 'set=', '"').rsplit("&", 1)[0]
        if not set_id:
            set_id = text.extr(set_ids_raw, '\\/photos\\/', '\\/')

        return set_id

    def items(self):
        profile_photos_url = (
            self.root + "/" + self.match.group(1) + "/photos_by"
        )
        profile_photos_page = self.request(profile_photos_url).text

        set_id = self.get_profile_photos_set_id(profile_photos_page)

        if set_id:
            set_url = self.set_url_fmt.format(set_id=set_id)
            set_page = self.request(set_url).text

            directory = self.get_set_page_metadata(set_page)

            yield Message.Directory, directory

            for photo in self.set_photos_iter(
                directory["first_photo_id"], directory["set_id"]
            ):
                yield Message.Url, photo["url"], photo
        else:
            self.log.debug("Profile photos set ID not found.")