# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Mastodon instances"""

from .common import BaseExtractor, Message
from .. import text


class MastodonExtractor(BaseExtractor):
    """Base class for mastodon extractors"""
    basecategory = "mastodon"
    directory_fmt = ("mastodon", "{instance}", "{account[username]}")
    filename_fmt = "{category}_{id}_{media[id]}.{extension}"
    archive_fmt = "{media[id]}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.item = self.groups[-1]

    def _init(self):
        self.api = self.utils().MastodonAPI(self)
        self.instance = self.root.partition("://")[2]
        self.reblogs = self.config("reblogs", False)
        self.replies = self.config("replies", True)
        self.cards = self.config("cards", False)

    def items(self):
        for status in self.statuses():

            if self._check_moved:
                self._check_moved(status["account"])
            if not self.reblogs and status["reblog"]:
                self.log.debug("Skipping %s (reblog)", status["id"])
                continue
            if not self.replies and status["in_reply_to_id"]:
                self.log.debug("Skipping %s (reply)", status["id"])
                continue

            attachments = status["media_attachments"]
            del status["media_attachments"]

            if status["reblog"]:
                attachments.extend(status["reblog"]["media_attachments"])

            if self.cards:
                if card := status.get("card"):
                    if url := card.get("image"):
                        card["weburl"] = card.get("url")
                        card["url"] = url
                        card["id"] = "card" + "".join(
                            url.split("/")[6:-2]).lstrip("0")
                        attachments.append(card)

            status["instance"] = self.instance
            acct = status["account"]["acct"]
            status["instance_remote"] = \
                acct.rpartition("@")[2] if "@" in acct else None

            status["count"] = len(attachments)
            status["tags"] = [tag["name"] for tag in status["tags"]]
            status["date"] = self.parse_datetime_iso(status["created_at"][:19])

            yield Message.Directory, status
            for status["num"], media in enumerate(attachments, 1):
                status["media"] = media
                url = media["url"]
                yield Message.Url, url, text.nameext_from_url(url, status)

    def statuses(self):
        """Return an iterable containing all relevant Status objects"""
        return ()

    def _check_moved(self, account):
        self._check_moved = None
        # Certain fediverse software (such as Iceshrimp and Sharkey) have a
        # null account "moved" field instead of not having it outright.
        # To handle this, check if the "moved" value is truthy instead
        # if only it exists.
        if account.get("moved"):
            self.log.warning("Account '%s' moved to '%s'",
                             account["acct"], account["moved"]["acct"])


BASE_PATTERN = MastodonExtractor.update({
    "mastodon.social": {
        "root"         : "https://mastodon.social",
        "pattern"      : r"mastodon\.social",
        "access-token" : "Y06R36SMvuXXN5_wiPKFAEFiQaMSQg0o_hGgc86Jj48",
        "client-id"    : "dBSHdpsnOUZgxOnjKSQrWEPakO3ctM7HmsyoOd4FcRo",
        "client-secret": "DdrODTHs_XoeOsNVXnILTMabtdpWrWOAtrmw91wU1zI",
    },
    "pawoo": {
        "root"         : "https://pawoo.net",
        "pattern"      : r"pawoo\.net",
        "access-token" : "c12c9d275050bce0dc92169a28db09d7"
                         "0d62d0a75a8525953098c167eacd3668",
        "client-id"    : "978a25f843ec01e53d09be2c290cd75c"
                         "782bc3b7fdbd7ea4164b9f3c3780c8ff",
        "client-secret": "9208e3d4a7997032cf4f1b0e12e5df38"
                         "8428ef1fadb446dcfeb4f5ed6872d97b",
    },
    "baraag": {
        "root"         : "https://baraag.net",
        "pattern"      : r"baraag\.net",
        "access-token" : "53P1Mdigf4EJMH-RmeFOOSM9gdSDztmrAYFgabOKKE0",
        "client-id"    : "czxx2qilLElYHQ_sm-lO8yXuGwOHxLX9RYYaD0-nq1o",
        "client-secret": "haMaFdMBgK_-BIxufakmI2gFgkYjqmgXGEO2tB-R2xY",
    }
}) + "(?:/web)?"


class MastodonUserExtractor(MastodonExtractor):
    """Extractor for all images of an account/user"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/(?:@|users/)([^/?#]+)(?:/media)?/?$"
    example = "https://mastodon.social/@USER"

    def statuses(self):
        return self.api.account_statuses(
            self.api.account_id_by_username(self.item),
            only_media=(
                not self.reblogs and
                not self.cards and
                not self.config("text-posts", False)
            ),
            exclude_replies=not self.replies,
        )


class MastodonBookmarkExtractor(MastodonExtractor):
    """Extractor for mastodon bookmarks"""
    subcategory = "bookmark"
    pattern = rf"{BASE_PATTERN}/bookmarks"
    example = "https://mastodon.social/bookmarks"

    def statuses(self):
        return self.api.account_bookmarks()


class MastodonFavoriteExtractor(MastodonExtractor):
    """Extractor for mastodon favorites"""
    subcategory = "favorite"
    pattern = rf"{BASE_PATTERN}/favourites"
    example = "https://mastodon.social/favourites"

    def statuses(self):
        return self.api.account_favorites()


class MastodonListExtractor(MastodonExtractor):
    """Extractor for mastodon lists"""
    subcategory = "list"
    pattern = rf"{BASE_PATTERN}/lists/(\w+)"
    example = "https://mastodon.social/lists/12345"

    def statuses(self):
        return self.api.timelines_list(self.item)


class MastodonHashtagExtractor(MastodonExtractor):
    """Extractor for mastodon hashtags"""
    subcategory = "hashtag"
    pattern = rf"{BASE_PATTERN}/tags/(\w+)"
    example = "https://mastodon.social/tags/NAME"

    def statuses(self):
        return self.api.timelines_tag(self.item)


class MastodonFollowingExtractor(MastodonExtractor):
    """Extractor for followed mastodon users"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/(?:@|users/)([^/?#]+)/following"
    example = "https://mastodon.social/@USER/following"

    def items(self):
        account_id = self.api.account_id_by_username(self.item)

        for account in self.api.account_following(account_id):
            account["_extractor"] = MastodonUserExtractor
            yield Message.Queue, account["url"], account


class MastodonStatusExtractor(MastodonExtractor):
    """Extractor for images from a status"""
    subcategory = "status"
    pattern = (rf"{BASE_PATTERN}/(?:@[^/?#]+|(?:users/[^/?#]+/)?"
               r"(?:statuses|notice|objects()))/(?!following)([^/?#]+)")
    example = "https://mastodon.social/@USER/12345"

    def statuses(self):
        if self.groups[-2] is not None:
            url = f"{self.root}/objects/{self.item}"
            location = self.request_location(url)
            self.item = location.rpartition("/")[2]
        return (self.api.status(self.item),)
