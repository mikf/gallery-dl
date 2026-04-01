# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.snapchat.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?snapchat\.com"
USER = r"(?:@|add/)([^/\?#]+)"
USER_PATTERN = BASE_PATTERN + r"/" + USER


class SnapchatExtractor(Extractor):
    """Base class for Snapchat extractors"""
    category = "snapchat"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = (
        "{date} {id}{num:?_//>02} {title[b:150]}{file_id:? [/]/}.{extension}")
    archive_fmt = "{date}_{id}_{num}_{file_id}"
    root = "https://www.snapchat.com"
    cookies_domain = ".snapchat.com"

    def _request_next_data(self, url):
        html = self.request(url).text
        data = self._extract_nextdata(html)
        return data["props"]["pageProps"]

    def _extract_avatar(self, next_data):
        metadata = next_data["userProfile"]["publicProfileInfo"].copy()

        url = metadata["profilePictureUrl"]
        text.nameext_from_url(url, metadata)
        try:
            timestamp = metadata["lastUpdateTimestampMs"]["value"]
        except (KeyError, TypeError):
            timestamp = metadata["creationTimestampMs"]["value"]
        # Ignore the milliseconds from the timestamp.
        timestamp = timestamp[:-3]

        metadata.update({
            "type"     : "avatar",
            # Unfortunately, the file extension is non-standard.
            # We'll need to overwrite it.
            "extension": "jpg",
            "date"     : self.parse_timestamp(timestamp),
            "id"       : metadata["username"],
            "file_id"  : url.rpartition("/")[2].rpartition(".")[0],
            "num"      : 0,
            "url"      : url,
            "user"     : next_data["user"],
        })

        return [url, metadata]

    def _extract_story_list(self, next_data):
        return next_data["curatedHighlights"].copy()

    def _extract_story(self, next_data):
        if "highlight" in next_data:
            return next_data["highlight"].copy()
        return next_data["story"].copy()

    def _extract_spotlight_list(self, next_data):
        return next_data["spotlightHighlights"].copy()

    def _extract_spotlight_feed(self, next_data):
        return next_data["spotlightFeed"]["spotlightStories"].copy()

    def _extract_post(self, data, item, default_title):
        url = item["snapUrls"]["mediaUrl"]
        text.nameext_from_url(url, data)
        timestamp = item["timestampInSec"]["value"]
        # 0: image, 1: video.
        type = item["snapMediaType"]
        try:
            title = data["storyTitle"]["value"]
        except (KeyError, TypeError):
            title = default_title
        id = item["snapId"]["value"]
        if not id:
            if "highlightId" in data:
                id = data["highlightId"]["value"]
            else:
                id = data["storyId"]["value"]

        data.update({
            **item,
            "type"     : "image" if type == "0" else "video",
            # Unfortunately, the file extension is non-standard.
            # We'll need to overwrite it.
            "extension": "jpg" if type == "o" else "mp4",
            "date"     : self.parse_timestamp(timestamp),
            "id"       : id,
            "num"      : item["snapIndex"] + 1,
            "title"    : title,
            "file_id"  : url.partition("?")[0].rpartition("/")[2],
            "url"      : url,
        })

        return [url, data]

    def _extract_story_item(self, story_data, snap_item):
        return self._extract_post(story_data, snap_item,
                                  "Snapchat Story")

    def _extract_spotlight_item(self, spotlight_data, snap_item):
        return self._extract_post(spotlight_data, snap_item,
                                  "Snapchat Spotlight")


class SnapchatAvatarExtractor(SnapchatExtractor):
    """Extracts a Snapchat user's avatar"""
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://www.snapchat.com/@username/avatar"

    def items(self):
        user = self.groups[0]
        profile_url = f"{self.root}/@{user}"
        next_data = self._request_next_data(profile_url)
        next_data["user"] = user

        [avatar_url, next_data] = self._extract_avatar(next_data)
        yield Message.Directory, "", next_data
        yield Message.Url, avatar_url, next_data


class SnapchatStoryExtractor(SnapchatExtractor):
    """Extracts an individual or timed story"""
    subcategory = "story"
    # The {20,} stops /stories and /spotlights URLs from matching with this
    # one. It is used to match against "timed" stories such as this one:
    # https://www.snapchat.com/@snackattackshow/
    # PnJFM8uuTRWo90OsrEH5pwAAgeGZvd2RrZGxxAZ1I2NonAZ1I2NmfAAAAAA.
    pattern = USER_PATTERN + r"/(?:highlight/)?[^/\?#]{20,}"
    example = "https://www.snapchat.com/@username/highlight/" + \
        "c3050cba-2f43-4e06-8ac4-d79069bac22f"

    def items(self):
        next_data = self._request_next_data(self.url)
        story_data = self._extract_story(next_data)
        if "publicUserProfile" in next_data:
            story_data["user"] = next_data["publicUserProfile"]["username"]
        else:
            public_profile_info = next_data["userProfile"]["publicProfileInfo"]
            story_data["user"] = public_profile_info["username"]

        yield Message.Directory, "", story_data
        for num, snap in enumerate(story_data["snapList"]):
            try:
                [url, story_item_data] = self._extract_story_item(
                    story_data.copy(), snap)
                yield Message.Url, url, story_item_data
            except Exception as exc:
                self.log.traceback(exc)
                self.log.error("%s: Failed to extract story item %d (%s: %s)",
                               self.url, num + 1, exc.__class__.__name__, exc)


class SnapchatSpotlightExtractor(SnapchatExtractor):
    """Extracts an individual spotlight post"""
    subcategory = "spotlight"
    pattern = BASE_PATTERN + rf"/(?:{USER}/)?spotlight/[^/\?#]+"
    example = "https://www.snapchat.com/spotlight/" + \
        "W7_EDlXWTBiXAEEniNoMPwAAYdGFzb3FpYXVuAZqDMm6sAZqDMm6VAAAAAQ"

    def items(self):
        next_data = self._request_next_data(self.url)
        next_data = self._extract_spotlight_feed(next_data)
        spotlight_data = next_data[0]["story"].copy()
        spotlight_data["metadata"] = next_data[0]["metadata"].copy()
        creator = spotlight_data["metadata"]["videoMetadata"]["creator"]
        spotlight_data["user"] = creator["personCreator"]["username"]

        yield Message.Directory, "", spotlight_data
        for num, snap in enumerate(spotlight_data["snapList"]):
            try:
                [url, spotlight_item_data] = self._extract_spotlight_item(
                    spotlight_data.copy(), snap)
                yield Message.Url, url, spotlight_item_data
            except Exception as exc:
                self.log.traceback(exc)
                self.log.error("%s: Failed to extract spotlight item %d (%s: "
                               "%s)", self.url, num + 1,
                               exc.__class__.__name__, exc)


class SnapchatLimitedSupportExtractor(SnapchatExtractor):
    """Notifies the user that this subcategory is only partially supported"""
    _user_has_been_alerted = False

    def _init(self):
        if not SnapchatLimitedSupportExtractor._user_has_been_alerted:
            subcategory = self.subcategory
            if subcategory == "user":
                subcategory += "s"
            self.log.warning("Be aware that support for Snapchat %s is "
                             "limited, you may not be able to download every "
                             "post!", subcategory)
            SnapchatLimitedSupportExtractor._user_has_been_alerted = True


class SnapchatStoriesExtractor(SnapchatLimitedSupportExtractor):
    """Extracts every [known] story belonging to a single Snapchat
    user"""
    subcategory = "stories"
    pattern = USER_PATTERN + r"/(?:stories|highlights)"
    example = "https://www.snapchat.com/@username/stories"

    def items(self):
        user = self.groups[0]
        profile_url = f"{self.root}/@{user}"
        next_data = self._request_next_data(profile_url)
        next_data["user"] = user

        yield Message.Directory, "", next_data
        story_list = self._extract_story_list(next_data)
        for num, story in enumerate(story_list):
            for item_num, snap in enumerate(story["snapList"]):
                try:
                    [url, story_data] = self._extract_story_item(story.copy(),
                                                                 snap)
                    story_data["user"] = user
                    yield Message.Url, url, story_data
                except Exception as exc:
                    self.log.traceback(exc)
                    self.log.error("%s: Failed to extract item %d of story %d "
                                   "(%s: %s)", self.url, item_num + 1, num + 1,
                                   exc.__class__.__name__, exc)


class SnapchatSpotlightsExtractor(SnapchatLimitedSupportExtractor):
    """Extracts every [known] spotlight belonging to a single Snapchat
    user"""
    subcategory = "spotlights"
    pattern = USER_PATTERN + r"/spotlights"
    example = "https://www.snapchat.com/@username/spotlights"

    def items(self):
        user = self.groups[0]
        profile_url = f"{self.root}/@{user}"
        next_data = self._request_next_data(profile_url)
        next_data["user"] = user

        yield Message.Directory, "", next_data
        spotlight_list = self._extract_spotlight_list(next_data)
        for num, spotlight in enumerate(spotlight_list):
            for item_num, snap in enumerate(spotlight["snapList"]):
                try:
                    [url, spotlight_data] = self._extract_spotlight_item(
                        spotlight.copy(), snap)
                    spotlight_data["user"] = user
                    yield Message.Url, url, spotlight_data
                except Exception as exc:
                    self.log.traceback(exc)
                    self.log.error("%s: Failed to extract item %d of "
                                   "spotlight %d (%s: %s)", self.url,
                                   item_num + 1, num + 1,
                                   exc.__class__.__name__, exc)


class SnapchatUserExtractor(SnapchatLimitedSupportExtractor):
    """Extractor for a Snapchat user profile"""
    subcategory = "user"
    pattern = USER_PATTERN + r"$"
    example = "https://www.snapchat.com/@username"

    def items(self):
        user = self.groups[0]
        profile_url = f"{self.root}/@{user}"
        next_data = self._request_next_data(profile_url)
        next_data["user"] = user

        yield Message.Directory, "", next_data

        # Avatar.
        try:
            [avatar_url, avatar_data] = self._extract_avatar(next_data)
            yield Message.Url, avatar_url, avatar_data
        except Exception as exc:
            self.log.traceback(exc)
            self.log.error("%s: Failed to extract avatar (%s: %s)",
                           self.url, exc.__class__.__name__, exc)

        # Stories.
        story_list = self._extract_story_list(next_data)
        for num, story in enumerate(story_list):
            for item_num, snap in enumerate(story["snapList"]):
                try:
                    [url, story_data] = self._extract_story_item(story.copy(),
                                                                 snap)
                    story_data["user"] = user
                    yield Message.Url, url, story_data
                except Exception as exc:
                    self.log.traceback(exc)
                    self.log.error("%s: Failed to extract item %d of story "
                                   "%d (%s: %s)", self.url, item_num + 1,
                                   num + 1, exc.__class__.__name__, exc)

        # Spotlight.
        spotlight_list = self._extract_spotlight_list(next_data)
        for num, spotlight in enumerate(spotlight_list):
            for item_num, snap in enumerate(spotlight["snapList"]):
                try:
                    [url, spotlight_data] = self._extract_spotlight_item(
                        spotlight.copy(), snap)
                    spotlight_data["user"] = user
                    yield Message.Url, url, spotlight_data
                except Exception as exc:
                    self.log.traceback(exc)
                    self.log.error("%s: Failed to extract item %d of "
                                   "spotlight %d (%s: %s)", self.url,
                                   item_num + 1, num + 1,
                                   exc.__class__.__name__, exc)
