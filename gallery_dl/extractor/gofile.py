# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from .common import Extractor, Message
from .. import exception
from ..cache import memcache


class GofileFolderExtractor(Extractor):
    category = "gofile"
    subcategory = "folder"
    root = "https://gofile.io"
    directory_fmt = ("{category}", "{name} ({code})")
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?(?:www\.)?gofile\.io/d/([^/?#]+)"
    test = (
        ("https://gofile.io/d/5qHmQj", {
            "pattern": r"https://file\d+\.gofile\.io/download"
                       r"/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
                       r"/test-%E3%83%86%E3%82%B9%E3%83%88-%2522%26!\.png",
            "keyword": {
                "createTime": int,
                "directLink": "re:https://store3.gofile.io/download/direct/.+",
                "downloadCount": int,
                "extension": "png",
                "filename": "test-テスト-%22&!",
                "folder": {
                    "childs": [
                        "346429cc-aee4-4996-be3f-e58616fe231f",
                        "765b6b12-b354-4e14-9a45-f763fa455682",
                        "2a44600a-4a59-4389-addc-4a0d542c457b"
                    ],
                    "code": "5qHmQj",
                    "createTime": 1648536501,
                    "id": "45cd45d1-dc78-4553-923f-04091c621699",
                    "isRoot": True,
                    "name": "root",
                    "public": True,
                    "totalDownloadCount": int,
                    "totalSize": 364,
                    "type": "folder"
                },
                "id": r"re:\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",
                "link": r"re:https://file17.gofile.io/download/.+\.png",
                "md5": "re:[0-9a-f]{32}",
                "mimetype": "image/png",
                "name": "test-テスト-%22&!.png",
                "num": int,
                "parentFolder": "45cd45d1-dc78-4553-923f-04091c621699",
                "serverChoosen": "file17",
                "size": 182,
                "thumbnail": r"re:https://store3.gofile.io/download/.+\.png",
                "type": "file"
            },
        }),
        ("https://gofile.io/d/346429cc-aee4-4996-be3f-e58616fe231f", {
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.content_id = match.group(1)

    def items(self):
        recursive = self.config("recursive")

        token = self.config("api-token")
        if token is None:
            self.log.debug("creating temporary account")
            token = self._create_account()
        self.session.cookies.set("accountToken", token, domain=".gofile.io")

        folder = self._get_content(self.content_id, token)
        yield Message.Directory, folder

        num = 0
        contents = folder.pop("contents")
        for content_id in folder["childs"]:
            content = contents[content_id]
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
        return self._api_request("createAccount")["token"]

    def _get_content(self, content_id, token):
        return self._api_request("getContent", {
            "contentId"   : content_id,
            "token"       : token,
            "websiteToken": "websiteToken",
        })

    def _api_request(self, endpoint, params=None):
        response = self.request(
            "https://api.gofile.io/" + endpoint, params=params).json()

        if response["status"] != "ok":
            if response["status"] == "error-notFound":
                raise exception.NotFoundError("content")
            raise exception.StopExtraction(
                "%s failed (Status: %s)", endpoint, response["status"])

        return response["data"]
