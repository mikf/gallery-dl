# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for mastodon instances"""

from .common import Extractor, Message
from .. import text, config, exception
import re


class MastodonExtractor(Extractor):
    """Base class for mastodon extractors"""
    basecategory = "mastodon"
    directory_fmt = ["mastodon", "{instance}", "{account[username]}"]
    filename_fmt = "{category}_{id}_{media[id]}.{extension}"
    archive_fmt = "{media[id]}"
    instance = None

    def __init__(self, match):
        Extractor.__init__(self)
        self.instance = match.group(1)
        self.api = MastodonAPI(self, self.instance)

    def config(self, key, default=None, *, sentinel=object()):
        value = Extractor.config(self, key, sentinel)
        if value is not sentinel:
            return value
        return config.interpolate(
            ("extractor", "mastodon", self.instance, self.subcategory, key),
            default,
        )

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
        return ()

    def prepare(self, status):
        """Prepare a status object"""
        status["instance"] = self.instance
        status["tags"] = [tag["name"] for tag in status["tags"]]
        attachments = status["media_attachments"]
        del status["media_attachments"]
        return attachments


class MastodonUserExtractor(MastodonExtractor):
    """Extractor for all images of an account/user"""
    subcategory = "user"

    def __init__(self, match):
        MastodonExtractor.__init__(self, match)
        self.account_name = match.group(2)

    def statuses(self):
        results = self.api.account_search("@" + self.account_name, 1)
        for account in results:
            if account["username"] == self.account_name:
                break
        else:
            raise exception.NotFoundError("account")
        return self.api.account_statuses(account["id"])


class MastodonStatusExtractor(MastodonExtractor):
    """Extractor for images from a status"""
    subcategory = "status"

    def __init__(self, match):
        MastodonExtractor.__init__(self, match)
        self.status_id = match.group(2)

    def statuses(self):
        return (self.api.status(self.status_id),)


class MastodonAPI():
    """Minimal interface for the Mastodon API

    https://github.com/tootsuite/mastodon
    https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md
    """

    def __init__(self, extractor, instance, access_token=None):
        self.instance = instance
        self.extractor = extractor
        self.headers = {"Authorization": "Bearer {}".format(
            extractor.config("access-token", access_token))}

    def account_search(self, query, limit=40):
        """Search for content"""
        params = {"q": query, "limit": limit}
        return self._call("accounts/search", params)

    def account_statuses(self, account_id):
        """Get an account's statuses"""
        endpoint = "accounts/{}/statuses".format(account_id)
        params = {"only_media": "1"}
        return self._pagination(endpoint, params)

    def status(self, status_id):
        """Fetch a Status"""
        return self._call("statuses/" + status_id)

    def _call(self, endpoint, params=None):
        url = "https://{}/api/v1/{}".format(self.instance, endpoint)
        response = self.extractor.request(
            url, params=params, headers=self.headers)
        return self._parse(response)

    def _pagination(self, endpoint, params):
        url = "https://{}/api/v1/{}".format(self.instance, endpoint)
        while url:
            response = self.extractor.request(
                url, params=params, headers=self.headers)
            yield from self._parse(response)
            url = response.links.get("next", {}).get("url")

    @staticmethod
    def _parse(response):
        """Parse an API response"""
        if response.status_code == 404:
            raise exception.NotFoundError()
        return response.json()


def generate_extractors():
    """Dynamically generate Extractor classes for Mastodon instances"""

    symtable = globals()
    mastodon = config.get(("extractor", "mastodon"))

    if not mastodon:
        mastodon = {}
        config.set(("extractor", "mastodon"), mastodon)
    if "pawoo.net" not in mastodon:
        mastodon["pawoo.net"] = {
            "category"     : "pawoo",
            "access-token" : "286462927198d0cf3e24683e91c8259a"
                             "ac4367233064e0570ca18df2ac65b226",
            "client-id"    : "97b142b6904abf97a1068d51a7bc2f2f"
                             "cf9323cef81f13cb505415716dba7dac",
            "client-secret": "e45bef4bad45b38abf7d9ef88a646b73"
                             "75e7fb2532c31a026327a93549236481",
        }

    for instance, info in mastodon.items():

        if not isinstance(info, dict):
            continue

        class UserExtractor(MastodonUserExtractor):
            pattern = [r"(?:https?://)?({})/@([^/?&#]+)(?:/media)?/?$".format(
                re.escape(instance))]

        class StatusExtractor(MastodonStatusExtractor):
            pattern = [r"(?:https?://)?({})/@[^/?&#]+/(\d+)".format(
                re.escape(instance))]

        category = info.get("category", instance)
        name = re.sub(r"[^A-Za-z]+", "", category).capitalize()

        for extr in (UserExtractor, StatusExtractor):
            extr.category = category
            extr.__name__ = name + extr.__name__
            extr.__doc__ = "{} on {}".format(extr.__base__.__doc__, instance)
            symtable[extr.__name__] = extr


generate_extractors()
