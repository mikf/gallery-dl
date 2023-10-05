# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fantia.jp/"""

from .common import Extractor, Message
from .. import text, util


class FantiaExtractor(Extractor):
    """Base class for Fantia extractors"""
    category = "fantia"
    root = "https://fantia.jp"
    directory_fmt = ("{category}", "{fanclub['id']}")
    filename_fmt = "{id}_{file_id}.{extension}"
    archive_fmt = "{id}_{file_id}"
    _warning = True

    def _init(self):
        self.headers = {
            "Accept" : "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
        }
        self._empty_plan = {
            "id"   : 0,
            "price": 0,
            "limit": 0,
            "name" : "",
            "description": "",
            "thumb": self.root + "/images/fallback/plan/thumb_default.png",
        }
        self._template_post = {
            "id": None,
            "title": None,
            "comment": None,
            "rating": None,
            "thumb": {
                "main": None,
                "original": None
            },
            "posted_at": None,
            "fanclub": {
                "id": None,
                "user": {
                    "id": None,
                    "name": None,
                    "image": {
                        "large": None
                    }
                },
                "name": None,
                "creator_name": None,
                "title": None,
                "cover": {
                    "main": None,
                    "original": None
                },
                "icon": {
                    "main": None,
                    "original": None
                },
            },
            "tags": None
        }
        if self._warning:
            if not self.cookies_check(("_session_id",)):
                self.log.warning("no '_session_id' cookie set")
            FantiaExtractor._warning = False

    def items(self):
        for post_id in self.posts():
            post = self._get_post_data(post_id)
            post["num"] = 0

            for content in self._get_post_contents(post):
                files = self._process_content(post, content)
                yield Message.Directory, post

                if content["visible_status"] != "visible":
                    self.log.warning(
                        "Unable to download '%s' files from "
                        "%s#post-content-id-%s", content["visible_status"],
                        post["post_url"], content["id"])

                for file in files:
                    post.update(file)
                    post["num"] += 1
                    text.nameext_from_url(
                        post["content"]["filename"] or file["file_url"], post)
                    yield Message.Url, file["file_url"], post

    def posts(self):
        """Return post IDs"""

    def _pagination(self, url):
        params = {"page": 1}

        while True:
            page = self.request(url, params=params).text
            self._csrf_token(page)

            post_id = None
            for post_id in text.extract_iter(
                    page, 'class="link-block" href="/posts/', '"'):
                yield post_id

            if not post_id:
                return
            params["page"] += 1

    def _csrf_token(self, page=None):
        if not page:
            page = self.request(self.root + "/").text
        self.headers["X-CSRF-Token"] = text.extr(
            page, 'name="csrf-token" content="', '"')

    def _build_new_dict(self, data, structure):
        new_data = {}
        for key, value in structure.items():
            if key in data:
                if isinstance(value, dict) and isinstance(data[key], dict):
                    new_data[key] = self._build_new_dict(data[key], value)
                elif value is None:
                    new_data[key] = data[key]
        return new_data

    def _get_post_data(self, post_id):
        """Fetch and process post data"""
        url = self.root + "/api/v1/posts/" + post_id
        resp = self.request(url, headers=self.headers).json()["post"]
        modified_resp = self._build_new_dict(resp, self._template_post)
        modified_resp.update(
            {
                "post_url": self.root + "/posts/" + str(resp["id"]),
                "date": text.parse_datetime(
                    resp["posted_at"], "%a, %d %b %Y %H:%M:%S %z"),
                "_data": resp["post_contents"],
                "content": {}
            }
        )

        return modified_resp

    def _get_post_contents(self, post):
        contents = post["_data"]

        try:
            url = post["thumb"]["original"]
        except Exception:
            pass
        else:
            contents.insert(0, {
                "id": "thumb",
                "title": "thumb",
                "visible_status": "visible",
                "category": "thumb",
                "download_uri": url,
                "plan": None,
            })

        return contents

    def _process_content(self, post, content):
        post["content"]["id"] = content["id"]
        post["content"]["title"] = content["title"]
        post["content"]["visible_status"] = content["visible_status"]
        post["content"]["category"] = content["category"]
        post["content"]["filename"] = content.get("filename") or ""
        post["content"]["comment"] = content.get("comment") or ""
        post["plan"] = content["plan"] or self._empty_plan

        files = []

        if "post_content_photos" in content:
            for photo in content["post_content_photos"]:
                files.append({"file_id" : photo["id"],
                              "file_url": photo["url"]["original"]})

        if "download_uri" in content:
            url = content["download_uri"]
            if url[0] == "/":
                url = self.root + url
            files.append({"file_id" : content["id"],
                          "file_url": url})

        if content["category"] == "blog" and "comment" in content:
            comment_json = util.json_loads(content["comment"])

            blog_text = ""
            for op in comment_json.get("ops") or ():
                insert = op.get("insert")
                if isinstance(insert, str):
                    blog_text += insert
                elif isinstance(insert, dict) and "fantiaImage" in insert:
                    img = insert["fantiaImage"]
                    files.append({"file_id" : img["id"],
                                  "file_url": self.root + img["original_url"]})
            post["blogpost_text"] = blog_text
        else:
            post["blogpost_text"] = ""

        return files


class FantiaCreatorExtractor(FantiaExtractor):
    """Extractor for a Fantia creator's works"""
    subcategory = "creator"
    pattern = r"(?:https?://)?(?:www\.)?fantia\.jp/fanclubs/(\d+)"
    example = "https://fantia.jp/fanclubs/12345"

    def __init__(self, match):
        FantiaExtractor.__init__(self, match)
        self.creator_id = match.group(1)

    def posts(self):
        url = "{}/fanclubs/{}/posts".format(self.root, self.creator_id)
        return self._pagination(url)


class FantiaPostExtractor(FantiaExtractor):
    """Extractor for media from a single Fantia post"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?fantia\.jp/posts/(\d+)"
    example = "https://fantia.jp/posts/12345"

    def __init__(self, match):
        FantiaExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        self._csrf_token()
        return (self.post_id,)
