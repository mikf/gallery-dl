# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://pawoo.net"""

from .common import Extractor, Message
from .. import text, exception


class PawooExtractor(Extractor):
    """Base class for pawoo extractors"""
    category = "pawoo"
    directory_fmt = ["{category}", "{account[username]}"]
    filename_fmt = "{category}_{id}_{media[id]}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = MastodonAPI(self.session, self.log)

    def items(self):
        yield Message.Version, 1
        for status in self.statuses():
            attachments = self.prepare(status)
            yield Message.Directory, status
            for media in attachments:
                status["media"] = media
                url = media["url"]
                yield Message.Url, url, text.nameext_from_url(url, status)

    def statuses(self):
        """Return an iterable containing all relevant Status-objects"""
        return []

    @staticmethod
    def prepare(status):
        """Prepare a status object"""
        for key in ("favourites_count", "reblogs_count", "reblog", "mentions"):
            del status[key]
        account = status["account"]
        for key in ("followers_count", "following_count", "statuses_count",
                    "oauth_authentications"):
            del account[key]
        attachments = status["media_attachments"]
        del status["media_attachments"]
        return attachments


class PawooAccountExtractor(PawooExtractor):
    """Extractor for all images of an account/user on pawoo.net"""
    subcategory = "account"
    pattern = [r"(?:https?://)?pawoo\.net/(@[^/]+)/?$"]
    test = [
        ("https://pawoo.net/@kuroda", {
            "url": "a3f9e7555f2b024554c0e9b6cbcc7991af13cf99",
            "keyword": "1b4e0dc5ac6c22ce9485ba12ecc200d0aaa2ffae",
        }),
        ("https://pawoo.net/@zZzZz/", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PawooExtractor.__init__(self)
        self.account_name = match.group(1)

    def statuses(self):
        results = self.api.search(self.account_name)
        for account in results["accounts"]:
            if account["username"] == self.account_name[1:]:
                break
        else:
            raise exception.NotFoundError("account")
        return self.api.account_statuses(account["id"])


class PawooStatusExtractor(PawooExtractor):
    """Extractor for images from a status on pawoo.net"""
    subcategory = "status"
    pattern = [r"(?:https?://)?pawoo\.net/@[^/]+/(\d+)"]
    test = [
        ("https://pawoo.net/@takehana_note/559043", {
            "url": "f95cc8c0274c4143e7e21dbdc693b90c65b596e3",
            "keyword": "7d060d9c4572b381aa423797ad48d89a12daac77",
            "content": "3b148cf90174173355fe34179741ce476921b2fc",
        }),
        ("https://pawoo.net/@zZzZz/12346", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PawooExtractor.__init__(self)
        self.status_id = match.group(1)

    def statuses(self):
        return (self.api.status(self.status_id),)


class MastodonAPI():
    """Minimal interface for the Mastodon API on pawoo.net

    https://github.com/tootsuite/mastodon
    https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md
    """

    def __init__(self, session, log, root="https://pawoo.net",
                 access_token=("0f04191976cf22a5319c1e91a73cbcb2"
                               "510b589e2757efcca922f9b3173d119b")):
        self.session = session
        self.session.headers["Authorization"] = "Bearer " + access_token
        self.log = log
        self.root = root

    def search(self, searchterm):
        """Search for content"""
        response = self.session.get(
            self.root + "/api/v1/search",
            params={"q": searchterm},
        )
        return self._parse(response)

    def status(self, status_id):
        """Fetch a Status"""
        response = self.session.get(
            self.root + "/api/v1/statuses/" + status_id
        )
        return self._parse(response)

    def account_statuses(self, account_id):
        """Get an account's statuses"""
        url = "{}/api/v1/accounts/{}/statuses?only_media=1".format(
            self.root, account_id)
        while True:
            response = self.session.get(url)
            yield from self._parse(response)
            url = response.links.get("next", {}).get("url")
            if not url:
                break

    @staticmethod
    def _parse(response):
        """Parse an API response"""
        if response.status_code == 404:
            raise exception.NotFoundError()
        return response.json()
