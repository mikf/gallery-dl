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
    directory_fmt = ("{category}", "{fanclub_id}")
    filename_fmt = "{post_id}_{file_id}.{extension}"
    archive_fmt = "{post_id}_{file_id}"
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
        if self._warning:
            if not self.cookies_check(("_session_id",)):
                self.log.warning("no '_session_id' cookie set")
            FantiaExtractor._warning = False

    def items(self):
        for post_id in self.posts():
            post = self._get_post_data(post_id)
            post["num"] = 0

            contents = self._get_post_contents(post)
            post["content_count"] = len(contents)
            post["content_num"] = 0

            for content in contents:
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
                        post["content_filename"] or file["file_url"], post)
                    yield Message.Url, file["file_url"], post

            post["content_num"] += 1

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

    def _get_post_data(self, post_id):
        """Fetch and process post data"""
        url = self.root+"/api/v1/posts/"+post_id
        resp = self.request(url, headers=self.headers).json()["post"]
        return {
            "post_id": resp["id"],
            "post_url": self.root + "/posts/" + str(resp["id"]),
            "post_title": resp["title"],
            "comment": resp["comment"],
            "rating": resp["rating"],
            "posted_at": resp["posted_at"],
            "date": text.parse_datetime(
                resp["posted_at"], "%a, %d %b %Y %H:%M:%S %z"),
            "fanclub_id": resp["fanclub"]["id"],
            "fanclub_user_id": resp["fanclub"]["user"]["id"],
            "fanclub_user_name": resp["fanclub"]["user"]["name"],
            "fanclub_name": resp["fanclub"]["name"],
            "fanclub_url": self.root+"/fanclubs/"+str(resp["fanclub"]["id"]),
            "tags": [t["name"] for t in resp["tags"]],
            "_data": resp,
        }

    def _get_post_contents(self, post):
        contents = post["_data"]["post_contents"]

        try:
            url = post["_data"]["thumb"]["original"]
        except Exception:
            pass
        else:
            contents.insert(0, {
                "id": "thumb",
                "title": "thumb",
                "category": "thumb",
                "download_uri": url,
                "visible_status": "visible",
                "plan": None,
            })

        return contents

    def _process_content(self, post, content):
        post["content_category"] = content["category"]
        post["content_title"] = content["title"]
        post["content_filename"] = content.get("filename") or ""
        post["content_id"] = content["id"]
        post["content_comment"] = content.get("comment") or ""
        post["content_num"] += 1
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
