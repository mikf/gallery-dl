# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for mastodon instances"""

from .common import Extractor, Message
from .. import text, util, config, exception
import re


class MastodonExtractor(Extractor):
    """Base class for mastodon extractors"""
    basecategory = "mastodon"
    directory_fmt = ("mastodon", "{instance}", "{account[username]}")
    filename_fmt = "{category}_{id}_{media[id]}.{extension}"
    archive_fmt = "{media[id]}"
    cookiedomain = None
    instance = None
    root = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = MastodonAPI(self)

    def config(self, key, default=None):
        return config.interpolate_common(
            ("extractor",), (
                (self.category, self.subcategory),
                (self.basecategory, self.instance, self.subcategory),
            ), key, default,
        )

    def items(self):
        yield Message.Version, 1
        for status in self.statuses():
            attachments = status["media_attachments"]
            if attachments:
                self.prepare(status)
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
        del status["media_attachments"]
        status["instance"] = self.instance
        status["tags"] = [tag["name"] for tag in status["tags"]]
        status["date"] = text.parse_datetime(
            status["created_at"][:19], "%Y-%m-%dT%H:%M:%S")


class MastodonUserExtractor(MastodonExtractor):
    """Extractor for all images of an account/user"""
    subcategory = "user"

    def __init__(self, match):
        MastodonExtractor.__init__(self, match)
        self.account_name = match.group(1)

    def statuses(self):
        handle = "@{}@{}".format(self.account_name, self.instance)
        for account in self.api.account_search(handle, 1):
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
        self.status_id = match.group(1)

    def statuses(self):
        return (self.api.status(self.status_id),)


class MastodonAPI():
    """Minimal interface for the Mastodon API

    https://github.com/tootsuite/mastodon
    https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md
    """

    def __init__(self, extractor, access_token=None):
        self.root = extractor.root
        self.extractor = extractor

        if not access_token:
            access_token = extractor.config(
                "access-token", extractor.access_token)
        self.headers = {"Authorization": "Bearer {}".format(access_token)}

    def account_search(self, query, limit=40):
        """Search for content"""
        params = {"q": query, "limit": limit}
        return self._call("accounts/search", params).json()

    def account_statuses(self, account_id):
        """Get an account's statuses"""
        endpoint = "accounts/{}/statuses".format(account_id)
        params = {"only_media": "1"}
        return self._pagination(endpoint, params)

    def status(self, status_id):
        """Fetch a Status"""
        return self._call("statuses/" + status_id).json()

    def _call(self, endpoint, params=None):
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = "{}/api/v1/{}".format(self.root, endpoint)

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)
            code = response.status_code

            if code < 400:
                return response
            if code == 404:
                raise exception.NotFoundError()
            if code == 429:
                self.extractor.wait(until=text.parse_datetime(
                    response.headers["x-ratelimit-reset"],
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                ))
                continue
            raise exception.StopExtraction(response.json().get("error"))

    def _pagination(self, endpoint, params):
        url = "{}/api/v1/{}".format(self.root, endpoint)
        while url:
            response = self._call(url, params)
            yield from response.json()

            url = response.links.get("next")
            if not url:
                return
            url = url["url"]


def generate_extractors():
    """Dynamically generate Extractor classes for Mastodon instances"""

    symtable = globals()
    extractors = config.get(("extractor",), "mastodon")
    if extractors:
        util.combine_dict(EXTRACTORS, extractors)
    config.set(("extractor",), "mastodon", EXTRACTORS)

    for instance, info in EXTRACTORS.items():

        if not isinstance(info, dict):
            continue

        category = info.get("category") or instance.replace(".", "")
        root = info.get("root") or "https://" + instance
        name = (info.get("name") or category).capitalize()
        token = info.get("access-token")
        pattern = info.get("pattern") or re.escape(instance)

        class Extr(MastodonUserExtractor):
            pass

        Extr.__name__ = Extr.__qualname__ = name + "UserExtractor"
        Extr.__doc__ = "Extractor for all images of a user on " + instance
        Extr.category = category
        Extr.instance = instance
        Extr.pattern = (r"(?:https?://)?" + pattern +
                        r"/@([^/?&#]+)(?:/media)?/?$")
        Extr.test = info.get("test-user")
        Extr.root = root
        Extr.access_token = token
        symtable[Extr.__name__] = Extr

        class Extr(MastodonStatusExtractor):
            pass

        Extr.__name__ = Extr.__qualname__ = name + "StatusExtractor"
        Extr.__doc__ = "Extractor for images from a status on " + instance
        Extr.category = category
        Extr.instance = instance
        Extr.pattern = r"(?:https?://)?" + pattern + r"/@[^/?&#]+/(\d+)"
        Extr.test = info.get("test-status")
        Extr.root = root
        Extr.access_token = token
        symtable[Extr.__name__] = Extr


EXTRACTORS = {
    "mastodon.social": {
        "category"     : "mastodon.social",
        "access-token" : "Y06R36SMvuXXN5_wiPKFAEFiQaMSQg0o_hGgc86Jj48",
        "client-id"    : "dBSHdpsnOUZgxOnjKSQrWEPakO3ctM7HmsyoOd4FcRo",
        "client-secret": "DdrODTHs_XoeOsNVXnILTMabtdpWrWOAtrmw91wU1zI",
        "test-user"    : ("https://mastodon.social/@jk", {
            "pattern": r"https://files.mastodon.social/media_attachments"
                       r"/files/(\d+/){3,}original/\w+",
            "range": "1-60",
            "count": 60,
        }),
        "test-status"  : ("https://mastodon.social/@jk/103794036899778366", {
            "count": 4,
        }),
    },
    "pawoo.net": {
        "category"     : "pawoo",
        "access-token" : "c12c9d275050bce0dc92169a28db09d7"
                         "0d62d0a75a8525953098c167eacd3668",
        "client-id"    : "978a25f843ec01e53d09be2c290cd75c"
                         "782bc3b7fdbd7ea4164b9f3c3780c8ff",
        "client-secret": "9208e3d4a7997032cf4f1b0e12e5df38"
                         "8428ef1fadb446dcfeb4f5ed6872d97b",
    },
    "baraag.net": {
        "category"     : "baraag",
        "access-token" : "53P1Mdigf4EJMH-RmeFOOSM9gdSDztmrAYFgabOKKE0",
        "client-id"    : "czxx2qilLElYHQ_sm-lO8yXuGwOHxLX9RYYaD0-nq1o",
        "client-secret": "haMaFdMBgK_-BIxufakmI2gFgkYjqmgXGEO2tB-R2xY",
    },
}


generate_extractors()
