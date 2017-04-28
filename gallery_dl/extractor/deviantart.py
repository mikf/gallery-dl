# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import time
import re


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors"""
    category = "deviantart"
    directory_fmt = ["{category}", "{username}"]
    filename_fmt = "{category}_{index}_{title}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = DeviantartAPI(self)
        self.offset = 0

    def skip(self, num):
        self.offset += num
        return num

    def items(self):
        first = True
        yield Message.Version, 1
        for deviation in self.deviations():
            if "content" not in deviation:
                continue
            if first:
                first = False
                yield Message.Directory, deviation["author"].copy()
            self.prepare(deviation)
            yield Message.Url, deviation["content"]["src"], deviation

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""
        return []

    @staticmethod
    def prepare(deviation):
        """Adjust the contents of a Deviation-object"""
        del deviation["stats"]
        deviation["index"] = deviation["url"].rsplit("-", 1)[1]
        text.nameext_from_url(deviation["content"]["src"], deviation)


class DeviantartUserExtractor(DeviantartExtractor):
    """Extractor for all works from an artist on deviantart.com"""
    subcategory = "user"
    pattern = [r"(?:https?://)?([^\.]+)\.deviantart\.com(?:/gallery)?/?$"]
    test = [("http://shimoda7.deviantart.com/gallery/", {
        "url": "63bfa8efba199e27181943c9060f6770f91a8441",
        "keyword": "ca77ad61f387be7dabb61eb322b5185bccec69ea",
    })]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.user = match.group(1)

    def deviations(self):
        return self.api.gallery_all(self.user, self.offset)


class DeviantartImageExtractor(DeviantartExtractor):
    """Extractor for single images from deviantart.com"""
    subcategory = "image"
    pattern = [r"(?:https?://)?([^\.]+\.deviantart\.com/art/.+-\d+)",
               r"(?:https?://)?(sta\.sh/[a-z0-9]+)"]
    test = [
        (("http://shimoda7.deviantart.com/art/"
          "For-the-sake-of-a-memory-10073852"), {
            "url": "71345ce3bef5b19bd2a56d7b96e6b5ddba747c2e",
            "keyword": "65f3c66cc1c9cf33757a71b86688fde4549fb045",
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://zzz.deviantart.com/art/zzz-1234567890", {
            "exception": exception.NotFoundError,
        }),
        ("http://sta.sh/01ijs78ebagf", {
            "url": "1692cd075059d24657a01b954413c84a56e2de8f",
            "keyword": "3faefb555d64e220e0e5526809e79bd4b9112eb2",
        }),
        ("http://sta.sh/abcdefghijkl", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.url = "https://" + match.group(1)

    def deviations(self):
        response = self.session.get(self.url)
        deviation_id = text.extract(response.text, '//deviation/', '"')[0]
        if response.status_code != 200 or not deviation_id:
            raise exception.NotFoundError("image")
        return (self.api.deviation(deviation_id),)


class DeviantartFavoriteExtractor(DeviantartExtractor):
    """Extractor for an artist's favourites from deviantart.com"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "{subcategory}",
                     "{collection[owner]} - {collection[title]}"]
    pattern = [r"(?:https?://)?([^\.]+)\.deviantart\.com/favourites"
               r"(?:/(\d+)/([^/?]+))?"]
    test = [
        ("http://h3813067.deviantart.com/favourites/", {
            "url": "71345ce3bef5b19bd2a56d7b96e6b5ddba747c2e",
            "keyword": "51e88d400c3fb69ae0b5a618ef21a282697185fe",
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("http://rosuuri.deviantart.com/favourites/58951174/Useful", {
            "url": "9e8d971c80db099b95d1c785399e2bc6eb96cd07",
            "keyword": "623dc7cf7178bcce57290931b2f99e21ba318bfd",
        }),
    ]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.user, self.favid, self.favname = match.groups()
        if not self.favname:
            self.favname = "Featured"
        self.collection = {
            "owner": self.user,
            "title": self.favname,
            "index": self.favid or 0,
        }

    def items(self):
        yield Message.Version, 1
        for deviation in self.deviations():
            if "content" not in deviation:
                continue
            self.prepare(deviation)
            yield Message.Directory, deviation
            yield Message.Url, deviation["content"]["src"], deviation

    def deviations(self):
        regex = re.compile(self.favname.replace("-", ".") + "$")
        for folder in self.api.collections_folders(self.user):
            if regex.match(folder["name"]):
                self.collection["title"] = folder["name"]
                return self.api.collections_folderid(
                    self.user, folder["folderid"], self.offset)
        raise exception.NotFoundError("collection")

    def prepare(self, deviation):
        DeviantartExtractor.prepare(deviation)
        deviation["collection"] = self.collection


class DeviantartAPI():
    """Minimal interface for the deviantart API"""
    def __init__(self, extractor, client_id="5388",
                 client_secret="76b08c69cfb27f26d6161f9ab6d061a1"):
        self.session = extractor.session
        self.session.headers["dA-minor-version"] = "20160316"
        self.log = extractor.log
        self.client_id = client_id
        self.client_secret = client_secret
        self.delay = 0

    def deviation(self, deviation_id):
        """Query and return info about a single Deviation"""
        endpoint = "deviation/" + deviation_id
        return self._call(endpoint)

    def gallery_all(self, username, offset=0):
        """Yield all Deviation-objects of a specific user"""
        endpoint = "gallery/all"
        params = {"username": username, "offset": offset, "limit": 10}
        return self._pagination(endpoint, params)

    def collections_folders(self, username, offset=0):
        """Yield all collection folders of a specific user"""
        endpoint = "collections/folders"
        params = {"username": username, "offset": offset, "limit": 10}
        return self._pagination(endpoint, params)

    def collections_folderid(self, username, folder_id, offset=0):
        """Yield all Deviation-objects contained in a collection folder"""
        endpoint = "collections/" + folder_id
        params = {"username": username, "offset": offset, "limit": 10}
        return self._pagination(endpoint, params)

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        access_token = self._authenticate_impl(
            self.client_id, self.client_secret
        )
        self.session.headers["Authorization"] = access_token

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, client_id, client_secret):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        response = self.session.post(url, data=data)
        if response.status_code != 200:
            raise exception.AuthenticationError()
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint, params=None):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2/" + endpoint
        tries = 1
        while True:
            if self.delay:
                time.sleep(self.delay)

            self.authenticate()
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                break
            elif response.status_code == 429:
                self.delay += 1
                self.log.debug("rate limit (delay: %d)", self.delay)
            else:
                self.delay = 1
                self.log.debug("http status code %d (%d/3)",
                               response.status_code, tries)
            tries += 1
            if tries > 3:
                raise Exception(response.text)
        try:
            return response.json()
        except ValueError:
            return {}

    def _pagination(self, endpoint, params=None):
        while True:
            data = self._call(endpoint, params)
            if "results" in data:
                yield from data["results"]
                if not data["has_more"]:
                    return
                params["offset"] = data["next_offset"]
            else:
                self.log.error("Unexpected API response: %s", data)
                return
