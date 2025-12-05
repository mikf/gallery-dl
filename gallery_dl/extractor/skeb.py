# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://skeb.jp/"""

from .common import Extractor, Message, Dispatch
from .. import text

BASE_PATTERN = r"(?:https?://)?skeb\.jp"
USER_PATTERN = rf"{BASE_PATTERN}/@([^/?#]+)"


class SkebExtractor(Extractor):
    """Base class for skeb extractors"""
    category = "skeb"
    directory_fmt = ("{category}", "{creator[screen_name]}")
    filename_fmt = "{post_num}_{file_id}.{extension}"
    archive_fmt = "{post_num}_{_file_id}_{content_category}"
    root = "https://skeb.jp"

    def _init(self):
        self.thumbnails = self.config("thumbnails", False)
        self.article = self.config("article", False)
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }

        if "Authorization" not in self.session.headers:
            self.headers["Authorization"] = "Bearer null"

    def _handle_429(self, response):
        if "request_key" in response.cookies:
            return True

        request_key = text.extr(
            response.text, "request_key=", ";")
        if request_key:
            self.cookies.set("request_key", request_key, domain="skeb.jp")
            return True

    def items(self):
        metadata = self.metadata()
        for user_name, post_num in self.posts():
            try:
                response, post = self._get_post_data(user_name, post_num)
            except Exception as exc:
                self.log.error("@%s/%s: %s: %s", user_name, post_num,
                               exc.__class__.__name__, exc)
                continue
            if metadata:
                post.update(metadata)

            files = self._get_files_from_post(response)
            post["count"] = len(files)
            yield Message.Directory, "", post
            for post["num"], file in enumerate(files, 1):
                post.update(file)
                url = file["file_url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def items_users(self):
        base = self.root + "/@"
        for user in self.users():
            user["_extractor"] = SkebUserExtractor
            yield Message.Queue, base + user["screen_name"], user

    def posts(self):
        """Return post number"""

    def metadata(self):
        """Return additional metadata"""

    def _pagination(self, url, params):
        params["offset"] = 0

        while True:
            posts = self.request_json(
                url, params=params, headers=self.headers)

            for post in posts:
                parts = post["path"].split("/")
                user_name = parts[1][1:]
                post_num = parts[3]

                if post["private"]:
                    self.log.debug("Skipping @%s/%s (private)",
                                   user_name, post_num)
                    continue
                yield user_name, post_num

            if len(posts) < 30:
                return
            params["offset"] += 30

    def _pagination_users(self, endpoint, params):
        url = f"{self.root}/api{endpoint}"
        params["offset"] = 0
        params["limit"] = 90

        while True:
            data = self.request_json(
                url, params=params, headers=self.headers)
            yield from data

            if len(data) < params["limit"]:
                return
            params["offset"] += params["limit"]

    def _get_post_data(self, user_name, post_num):
        url = f"{self.root}/api/users/{user_name}/works/{post_num}"
        resp = self.request_json(url, headers=self.headers)
        creator = resp["creator"]
        post = {
            "post_id"          : resp["id"],
            "post_num"         : post_num,
            "post_url"         : self.root + resp["path"],
            "body"             : resp["body"],
            "source_body"      : resp["source_body"],
            "translated_body"  : resp["translated"],
            "nsfw"             : resp["nsfw"],
            "anonymous"        : resp["anonymous"],
            "tags"             : resp["tag_list"],
            "genre"            : resp["genre"],
            "thanks"           : resp["thanks"],
            "source_thanks"    : resp["source_thanks"],
            "translated_thanks": resp["translated_thanks"],
            "creator": {
                "id"           : creator["id"],
                "name"         : creator["name"],
                "screen_name"  : creator["screen_name"],
                "avatar_url"   : creator["avatar_url"],
                "header_url"   : creator["header_url"],
            }
        }
        if not resp["anonymous"] and "client" in resp:
            client = resp["client"]
            post["client"] = {
                "id"           : client["id"],
                "name"         : client["name"],
                "screen_name"  : client["screen_name"],
                "avatar_url"   : client["avatar_url"],
                "header_url"   : client["header_url"],
            }
        return resp, post

    def _get_files_from_post(self, resp):
        files = []

        if self.thumbnails and "og_image_url" in resp:
            files.append({
                "content_category": "thumb",
                "file_id" : "thumb",
                "_file_id": str(resp["id"]) + "t",
                "file_url": resp["og_image_url"],
            })

        if self.article and "article_image_url" in resp:
            if url := resp["article_image_url"]:
                files.append({
                    "content_category": "article",
                    "file_id" : "article",
                    "_file_id": str(resp["id"]) + "a",
                    "file_url": url,
                })

        for preview in resp["previews"]:
            info = preview["information"]
            files.append({
                "content_category": "preview",
                "file_id" : preview["id"],
                "_file_id": preview["id"],
                "file_url": preview["url"],
                "original": {
                    "width"     : info["width"],
                    "height"    : info["height"],
                    "byte_size" : info["byte_size"],
                    "duration"  : info["duration"],
                    "frame_rate": info.get("frame_rate"),
                    "software"  : info["software"],
                    "extension" : info["extension"],
                    "is_movie"  : info["is_movie"],
                    "transcoder": info["transcoder"],
                },
            })

        return files


class SkebPostExtractor(SkebExtractor):
    """Extractor for a single skeb post"""
    subcategory = "post"
    pattern = rf"{USER_PATTERN}/works/(\d+)"
    example = "https://skeb.jp/@USER/works/123"

    def posts(self):
        return (self.groups,)


class SkebWorksExtractor(SkebExtractor):
    """Extractor for a skeb user's works"""
    subcategory = "works"
    pattern = rf"{USER_PATTERN}/works"
    example = "https://skeb.jp/@USER/works"

    def posts(self):
        url = f"{self.root}/api/users/{self.groups[0]}/works"
        params = {"role": "creator", "sort": "date"}
        return self._pagination(url, params)


class SkebSentrequestsExtractor(SkebExtractor):
    """Extractor for a skeb user's sent requests"""
    subcategory = "sentrequests"
    pattern = rf"{USER_PATTERN}/sent[ _-]?requests"
    example = "https://skeb.jp/@USER/sentrequests"

    def posts(self):
        url = f"{self.root}/api/users/{self.groups[0]}/works"
        params = {"role": "client", "sort": "date"}
        return self._pagination(url, params)


class SkebUserExtractor(Dispatch, SkebExtractor):
    """Extractor for a skeb user profile"""
    pattern = rf"{USER_PATTERN}/?$"
    example = "https://skeb.jp/@USER"

    def items(self):
        if self.config("sent-requests", False):
            default = ("works", "sentrequests")
        else:
            default = ("works",)

        base = f"{self.root}/@{self.groups[0]}/"
        return self._dispatch_extractors((
            (SkebWorksExtractor       , base + "works"),
            (SkebSentrequestsExtractor, base + "sentrequests"),
        ), default)


class SkebSearchExtractor(SkebExtractor):
    """Extractor for skeb search results"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search\?q=([^&#]+)"
    example = "https://skeb.jp/search?q=QUERY"

    def metadata(self):
        return {"search_tags": text.unquote(self.groups[0])}

    def posts(self):
        url = "https://hb1jt3kre9-2.algolianet.com/1/indexes/*/queries"
        params = {
            "x-algolia-agent": "Algolia for JavaScript (4.13.1); Browser",
        }
        headers = {
            "Origin": self.root,
            "x-algolia-api-key": "9a4ce7d609e71bf29e977925e4c6740c",
            "x-algolia-application-id": "HB1JT3KRE9",
        }

        filters = self.config("filters")
        if filters is None:
            filters = ("genre:art OR genre:voice OR genre:novel OR "
                       "genre:video OR genre:music OR genre:correction")
        elif not isinstance(filters, str):
            filters = " OR ".join(filters)

        page = 0
        pams = "hitsPerPage=40&filters=" + text.quote(filters) + "&page="

        request = {
            "indexName": "Request",
            "query": text.unquote(self.groups[0]),
            "params": pams + str(page),
        }
        data = {"requests": (request,)}

        while True:
            result = self.request_json(
                url, method="POST", params=params, headers=headers, json=data,
            )["results"][0]

            for post in result["hits"]:
                parts = post["path"].split("/")
                yield parts[1][1:], parts[3]

            if page >= result["nbPages"]:
                return
            page += 1
            request["params"] = pams + str(page)


class SkebFollowingExtractor(SkebExtractor):
    """Extractor for all creators followed by a skeb user"""
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/following_creators"
    example = "https://skeb.jp/@USER/following_creators"

    items = SkebExtractor.items_users

    def users(self):
        endpoint = f"/users/{self.groups[0]}/following_creators"
        params = {"sort": "date"}
        return self._pagination_users(endpoint, params)


class SkebFollowingUsersExtractor(SkebExtractor):
    """Extractor for your followed users"""
    subcategory = "following-users"
    pattern = rf"{BASE_PATTERN}/following_users"
    example = "https://skeb.jp/following_users"

    items = SkebExtractor.items_users

    def users(self):
        endpoint = "/following_users"
        return self._pagination_users(endpoint, {})
