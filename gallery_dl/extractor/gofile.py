# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from .common import Extractor, Message
from .. import text, exception
from ..cache import memcache


class GofileFolderExtractor(Extractor):
    category = "gofile"
    subcategory = "folder"
    root = "https://gofile.io"
    directory_fmt = ("{category}", "{name} ({code})")
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?(?:www\.)?gofile\.io/d/([^/?#]+)"
    test = (
        ("https://gofile.io/d/k6BomI", {
            "pattern": r"https://store\d+\.gofile\.io/download"
                       r"/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
                       r"/test-%E3%83%86%E3%82%B9%E3%83%88-%2522%26!\.png",
            "keyword": {
                "createTime": int,
                "directLink": "re:https://store5.gofile.io/download/direct/.+",
                "downloadCount": int,
                "extension": "png",
                "filename": "test-テスト-%22&!",
                "folder": {
                    "childs": [
                        "b0367d79-b8ba-407f-8342-aaf8eb815443",
                        "7fd4a36a-c1dd-49ff-9223-d93f7d24093f"
                    ],
                    "code": "k6BomI",
                    "createTime": 1654076165,
                    "id": "fafb59f9-a7c7-4fea-a098-b29b8d97b03c",
                    "name": "root",
                    "public": True,
                    "totalDownloadCount": int,
                    "totalSize": 182,
                    "type": "folder"
                },
                "id": r"re:\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",
                "link": r"re:https://store5.gofile.io/download/.+\.png",
                "md5": "re:[0-9a-f]{32}",
                "mimetype": "image/png",
                "name": "test-テスト-%22&!.png",
                "num": int,
                "parentFolder": "fafb59f9-a7c7-4fea-a098-b29b8d97b03c",
                "serverChoosen": "store5",
                "size": 182,
                "thumbnail": r"re:https://store5.gofile.io/download/.+\.png",
                "type": "file"
            },
        }),
        ("https://gofile.io/d/7fd4a36a-c1dd-49ff-9223-d93f7d24093f", {
            "options": (("website-token", None),),
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.content_id = match.group(1)

    def items(self):
        recursive = self.config("recursive")

        token = self.config("api-token")
        if not token:
            token = self._create_account()
        self.session.cookies.set("accountToken", token, domain=".gofile.io")
        self.api_token = token

        token = self.config("website-token", "12345")
        if not token:
            token = self._get_website_token()
        self.website_token = token

        folder = self._get_content(self.content_id)
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
        self.log.debug("Creating temporary account")
        return self._api_request("createAccount")["token"]

    @memcache()
    def _get_website_token(self):
        self.log.debug("Fetching website token")
        page = self.request(self.root + "/contents/files.html").text
        return text.extract(page, "websiteToken:", ",")[0].strip("\" ")

    def _get_content(self, content_id):
        return self._api_request("getContent", {
            "contentId"   : content_id,
            "token"       : self.api_token,
            "websiteToken": self.website_token,
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
