# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
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
    archive_fmt = "{media[id]}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = MastodonAPI(self)

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
        attachments = status["media_attachments"]
        del status["media_attachments"]
        return attachments


class PawooUserExtractor(PawooExtractor):
    """Extractor for all images of an account/user on pawoo.net"""
    subcategory = "user"
    pattern = [r"(?:https?://)?pawoo\.net/@([^/?&#]+)(?:/media)?/?$"]
    test = [
        ("https://pawoo.net/@kuroda", {
            "url": "a3f9e7555f2b024554c0e9b6cbcc7991af13cf99",
        }),
        ("https://pawoo.net/@zZzZz/", {
            "exception": exception.NotFoundError,
        }),
        ("https://pawoo.net/@kuroda/media", None),
    ]

    def __init__(self, match):
        PawooExtractor.__init__(self)
        self.account_name = match.group(1)

    def statuses(self):
        results = self.api.account_search("@" + self.account_name, 1)
        for account in results:
            if account["username"] == self.account_name:
                break
        else:
            raise exception.NotFoundError("account")
        return self.api.account_statuses(account["id"])


class PawooStatusExtractor(PawooExtractor):
    """Extractor for images from a status on pawoo.net"""
    subcategory = "status"
    pattern = [r"(?:https?://)?pawoo\.net/@[^/?&#]+/(\d+)"]
    test = [
        ("https://pawoo.net/@takehana_note/559043", {
            "url": "f95cc8c0274c4143e7e21dbdc693b90c65b596e3",
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

    def __init__(self, extractor, root="https://pawoo.net",
                 access_token=("286462927198d0cf3e24683e91c8259a"
                               "ac4367233064e0570ca18df2ac65b226")):
        access_token = extractor.config("access-token", access_token)
        self.session = extractor.session
        self.session.headers["Authorization"] = "Bearer " + access_token
        self.root = root

    def account_search(self, query, limit=40):
        """Search for content"""
        response = self.session.get(
            self.root + "/api/v1/accounts/search",
            params={"q": query, "limit": limit},
        )
        return self._parse(response)

    def account_statuses(self, account_id):
        """Get an account's statuses"""
        url = "{}/api/v1/accounts/{}/statuses?only_media=1".format(
            self.root, account_id)
        while url:
            response = self.session.get(url)
            yield from self._parse(response)
            url = response.links.get("next", {}).get("url")

    def status(self, status_id):
        """Fetch a Status"""
        response = self.session.get(
            self.root + "/api/v1/statuses/" + status_id
        )
        return self._parse(response)

    @staticmethod
    def _parse(response):
        """Parse an API response"""
        if response.status_code == 404:
            raise exception.NotFoundError()
        return response.json()
