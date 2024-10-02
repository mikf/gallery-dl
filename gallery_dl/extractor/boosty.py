# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.boosty.to/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?boosty\.to"


class BoostyExtractor(Extractor):
    """Base class for boosty extractors"""
    category = "boosty"
    root = "https://www.boosty.to"
    directory_fmt = ("{category}", "{user[blogUrl]} ({user[id]})",
                     "{post[date]:%Y-%m-%d} {post[int_id]}")
    filename_fmt = "{num:>02} {file[id]}.{extension}"
    archive_fmt = "{file[id]}"
    cookies_domain = ".boosty.to"
    cookies_names = ("auth",)

    def _init(self):
        self.api = BoostyAPI(self)

        self._user = None if self.config("metadata") else False
        self.only_allowed = self.config("allowed", True)

        videos = self.config("videos")
        if videos is None:
            videos = ("quad_hd", "ultra_hd", "full_hd",
                      "high", "medium", "low")
        elif videos and isinstance(videos, str):
            videos = videos.split(",")
        self.videos = videos

    def items(self):
        for post in self.posts():
            if not post.get("hasAccess"):
                self.log.warning("Not allowed to access post %s", post["id"])
                continue

            files = self._process_post(post)
            data = {
                "post" : post,
                "user" : post.pop("user", None),
                "count": len(files),
            }

            yield Message.Directory, data
            for data["num"], file in enumerate(files, 1):
                data["file"] = file
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, data)

    def posts(self):
        """Yield JSON content of all relevant posts"""

    def _process_post(self, post):
        files = []
        post["content"] = content = []
        post["links"] = links = []

        if "createdAt" in post:
            post["date"] = text.parse_timestamp(post["createdAt"])
        if self._user:
            post["user"] = self._user

        for block in post["data"]:
            try:
                type = block["type"]
                if type == "text":
                    if block["modificator"] == "BLOCK_END":
                        continue
                    c = util.json_loads(block["content"])
                    content.append(c[0])

                elif type == "image":
                    files.append(block)

                elif type == "ok_video":
                    if not self.videos:
                        self.log.debug("%s: Skipping video %s",
                                       post["int_id"], block["id"])
                        continue
                    fmts = {
                        fmt["type"]: fmt["url"]
                        for fmt in block["playerUrls"]
                        if fmt["url"]
                    }
                    formats = [
                        fmts[fmt]
                        for fmt in self.videos
                        if fmt in fmts
                    ]
                    if formats:
                        formats = iter(formats)
                        block["url"] = next(formats)
                        block["_fallback"] = formats
                        files.append(block)
                    else:
                        self.log.warning(
                            "%s: Found no suitable video format for %s",
                            post["int_id"], block["id"])

                elif type == "link":
                    url = block["url"]
                    links.appens(url)
                    content.append(url)

                else:
                    self.log.debug("%s: Unsupported data type '%s'",
                                   post["int_id"], type)
            except Exception as exc:
                self.log.debug("%s: %s", exc.__class__.__name__, exc)

        del post["data"]
        return files


class BoostyUserExtractor(BoostyExtractor):
    """Extractor for boosty.to user profiles"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/([^/?#]+)(?:\?([^#]+))?$"
    example = "https://boosty.to/USER"

    def posts(self):
        user, query = self.groups
        params = text.parse_query(query)
        if self._user is None:
            self._user = self.api.user(user)
        return self.api.blog_posts(user, params)


class BoostyMediaExtractor(BoostyExtractor):
    """Extractor for boosty.to user media"""
    subcategory = "media"
    directory_fmt = "{category}", "{user[blogUrl]} ({user[id]})", "media"
    filename_fmt = "{post[id]}_{num}.{extension}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/media/([^/?#]+)(?:\?([^#]+))?"
    example = "https://boosty.to/USER/media/all"

    def posts(self):
        user, media, query = self.groups
        params = text.parse_query(query)
        self._user = self.api.user(user)
        return self.api.blog_media_album(user, media, params)


class BoostyPostExtractor(BoostyExtractor):
    """Extractor for boosty.to posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/([^/?#]+)/posts/([0-9a-f-]+)"
    example = "https://boosty.to/USER/posts/01234567-89ab-cdef-0123-456789abcd"

    def posts(self):
        user, post_id = self.groups
        if self._user is None:
            self._user = self.api.user(user)
        return (self.api.post(user, post_id),)


class BoostyAPI():
    """Interface for the Boosty API"""
    root = "https://api.boosty.to"

    def __init__(self, extractor, access_token=None):
        self.extractor = extractor
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": extractor.root,
        }

        if not access_token:
            auth = self.extractor.cookies.get("auth", domain=".boosty.to")
            if auth:
                access_token = text.extr(
                    auth, "%22accessToken%22%3A%22", "%22")
        if access_token:
            self.headers["Authorization"] = "Bearer " + access_token

    def blog_posts(self, username, params):
        endpoint = "/v1/blog/{}/post/".format(username)
        params = self._combine_params(params, {
            "limit"         : "5",
            "offset"        : None,
            "comments_limit": "2",
            "reply_limit"   : "1",
        })
        return self._pagination(endpoint, params)

    def blog_media_album(self, username, type="all", params=()):
        endpoint = "/v1/blog/{}/media_album/".format(username)
        params = self._combine_params(params, {
            "type"    : type.rstrip("s"),
            "limit"   : "15",
            "limit_by": "media",
            "offset"  : None,
        })
        return self._pagination(endpoint, params, self._transform_media_posts)

    def _transform_media_posts(self, data):
        posts = []

        for obj in data["mediaPosts"]:
            post = obj["post"]
            post["data"] = obj["media"]
            posts.append(post)

        return posts

    def post(self, username, post_id):
        endpoint = "/v1/blog/{}/post/{}".format(username, post_id)
        return self._call(endpoint)

    def user(self, username):
        endpoint = "/v1/blog/" + username
        user = self._call(endpoint)
        user["id"] = user["owner"]["id"]
        return user

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers,
                fatal=None, allow_redirects=False)

            if response.status_code < 300:
                return response.json()

            elif response.status_code < 400:
                raise exception.AuthenticationError("Invalid API access token")

            elif response.status_code == 429:
                self.extractor.wait(seconds=600)

            else:
                self.extractor.log.debug(response.text)
                raise exception.StopExtraction("API request failed")

    def _pagination(self, endpoint, params, transform=None):
        if "is_only_allowed" not in params and self.extractor.only_allowed:
            params["is_only_allowed"] = "true"

        while True:
            data = self._call(endpoint, params)

            if transform:
                yield from transform(data["data"])
            else:
                yield from data["data"]

            extra = data["extra"]
            if extra.get("isLast"):
                return
            offset = extra.get("offset")
            if not offset:
                return
            params["offset"] = offset

    def _combine_params(self, params_web, params_api):
        if params_web:
            params_api.update(self._web_to_api(params_web))
        return params_api

    def _web_to_api(self, params):
        return {
            api: params[web]
            for web, api in (
                ("isOnlyAllowedPosts", "is_only_allowed"),
                ("postsFrom", "from_ts"),
                ("postsTo", "to_ts"),
            )
            if web in params
        }
