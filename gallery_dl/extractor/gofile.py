# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://gofile.io/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache, memcache
import hashlib


class GofileFolderExtractor(Extractor):
    category = "gofile"
    subcategory = "folder"
    root = "https://gofile.io"
    directory_fmt = ("{category}", "{name} ({code})")
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?(?:www\.)?gofile\.io/d/([^/?#]+)"
    example = "https://gofile.io/d/ID"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.content_id = match.group(1)

    def items(self):
        recursive = self.config("recursive")
        password = self.config("password")

        token = self.config("api-token")
        if not token:
            token = self._create_account()
        self.cookies.set("accountToken", token, domain=".gofile.io")
        self.api_token = token

        self.website_token = (self.config("website-token") or
                              self._get_website_token())

        folder = self._get_content(self.content_id, password)
        yield Message.Directory, folder

        try:
            contents = folder.pop("children")
        except KeyError:
            raise exception.AuthorizationError("Password required")

        num = 0
        for content in contents.values():
            content["folder"] = folder

            if content["type"] == "file":
                num += 1
                content["num"] = num
                content["filename"], _, content["extension"] = \
                    content["name"].rpartition(".")
                yield Message.Url, content["link"], content

            elif content["type"] == "folder":
                if recursive:
                    url = "https://gofile.io/d/" + content["id"]
                    content["_extractor"] = GofileFolderExtractor
                    yield Message.Queue, url, content

            else:
                self.log.debug("'%s' is of unknown type (%s)",
                               content.get("name"), content["type"])

    @memcache()
    def _create_account(self):
        self.log.debug("Creating temporary account")
        return self._api_request("accounts", method="POST")["token"]

    @cache(maxage=86400)
    def _get_website_token(self):
        self.log.debug("Fetching website token")
        page = self.request(self.root + "/dist/js/global.js").text
        return text.extr(page, '.wt = "', '"')

    def _get_content(self, content_id, password=None):
        headers = {"Authorization": "Bearer " + self.api_token}
        params = {"wt": self.website_token}
        if password is not None:
            params["password"] = hashlib.sha256(password.encode()).hexdigest()
        return self._api_request("contents/" + content_id, params, headers)

    def _api_request(self, endpoint, params=None, headers=None, method="GET"):
        response = self.request(
            "https://api.gofile.io/" + endpoint,
            method=method, params=params, headers=headers,
        ).json()

        if response["status"] != "ok":
            if response["status"] == "error-notFound":
                raise exception.NotFoundError("content")
            if response["status"] == "error-passwordRequired":
                raise exception.AuthorizationError("Password required")
            raise exception.StopExtraction(
                "%s failed (Status: %s)", endpoint, response["status"])

        return response["data"]
