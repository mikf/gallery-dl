# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.boosty.to/"""

from .common import Extractor, Message
from .. import text, util, exception
import itertools

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
        self.only_bought = self.config("bought")

        videos = self.config("videos")
        if videos is None or videos:
            if isinstance(videos, str):
                videos = videos.split(",")
            elif not isinstance(videos, (list, tuple)):
                # ultra_hd: 2160p
                #  quad_hd: 1440p
                #  full_hd: 1080p
                #     high:  720p
                #   medium:  480p
                #      low:  360p
                #   lowest:  240p
                #     tiny:  144p
                videos = ("ultra_hd", "quad_hd", "full_hd",
                          "high", "medium", "low", "lowest", "tiny")
        self.videos = videos

    def items(self):
        for post in self.posts():
            if not post.get("hasAccess"):
                self.log.warning("Not allowed to access post %s", post["id"])
                continue

            files = self._extract_files(post)
            if self._user:
                post["user"] = self._user
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

    def _extract_files(self, post):
        files = []
        post["content"] = content = []
        post["links"] = links = []

        if "createdAt" in post:
            post["date"] = text.parse_timestamp(post["createdAt"])

        for block in post["data"]:
            try:
                type = block["type"]
                if type == "text":
                    if block["modificator"] == "BLOCK_END":
                        continue
                    c = util.json_loads(block["content"])
                    content.append(c[0])

                elif type == "image":
                    files.append(self._update_url(post, block))

                elif type == "ok_video":
                    if not self.videos:
                        self.log.debug("%s: Skipping video %s",
                                       post["id"], block["id"])
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
                            post["id"], block["id"])

                elif type == "link":
                    url = block["url"]
                    links.append(url)
                    content.append(url)

                elif type == "audio_file":
                    files.append(self._update_url(post, block))

                elif type == "file":
                    files.append(self._update_url(post, block))

                elif type == "smile":
                    content.append(":" + block["name"] + ":")

                else:
                    self.log.debug("%s: Unsupported data type '%s'",
                                   post["id"], type)
            except Exception as exc:
                self.log.debug("%s: %s", exc.__class__.__name__, exc)

        del post["data"]
        return files

    def _update_url(self, post, block):
        url = block["url"]
        sep = "&" if "?" in url else "?"

        signed_query = post.get("signedQuery")
        if signed_query:
            url += sep + signed_query[1:]
            sep = "&"

        migrated = post.get("isMigrated")
        if migrated is not None:
            url += sep + "is_migrated=" + str(migrated).lower()

        block["url"] = url
        return block


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


class BoostyFeedExtractor(BoostyExtractor):
    """Extractor for your boosty.to subscription feed"""
    subcategory = "feed"
    pattern = BASE_PATTERN + r"/(?:\?([^#]+))?(?:$|#)"
    example = "https://boosty.to/"

    def posts(self):
        params = text.parse_query(self.groups[0])
        return self.api.feed_posts(params)


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


class BoostyFollowingExtractor(BoostyExtractor):
    """Extractor for your boosty.to subscribed users"""
    subcategory = "following"
    pattern = BASE_PATTERN + r"/app/settings/subscriptions"
    example = "https://boosty.to/app/settings/subscriptions"

    def items(self):
        for user in self.api.user_subscriptions():
            url = "{}/{}".format(self.root, user["blog"]["blogUrl"])
            user["_extractor"] = BoostyUserExtractor
            yield Message.Queue, url, user


class BoostyDirectMessagesExtractor(BoostyExtractor):
    """Extractor for boosty.to direct messages"""
    subcategory = "direct-messages"
    directory_fmt = ("{category}", "{user[blogUrl]} ({user[id]})",
                     "Direct Messages")
    pattern = BASE_PATTERN + r"/app/messages/?\?dialogId=(\d+)"
    example = "https://boosty.to/app/messages?dialogId=12345"

    def items(self):
        """Yield direct messages from a given dialog ID."""
        dialog_id = self.groups[0]
        response = self.api.dialog(dialog_id)
        signed_query = response.get("signedQuery")

        try:
            messages = response["messages"]["data"]
            offset = messages[0]["id"]
        except Exception:
            return

        try:
            user = self.api.user(response["chatmate"]["url"])
        except Exception:
            user = None

        messages.reverse()
        for message in itertools.chain(
            messages,
            self.api.dialog_messages(dialog_id, offset=offset)
        ):
            message["signedQuery"] = signed_query
            files = self._extract_files(message)
            data = {
                "post": message,
                "user": user,
                "count": len(files),
            }

            yield Message.Directory, data
            for data["num"], file in enumerate(files, 1):
                data["file"] = file
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, data)


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
        params = self._merge_params(params, {
            "limit"         : "5",
            "offset"        : None,
            "comments_limit": "2",
            "reply_limit"   : "1",
        })
        return self._pagination(endpoint, params)

    def blog_media_album(self, username, type="all", params=()):
        endpoint = "/v1/blog/{}/media_album/".format(username)
        params = self._merge_params(params, {
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

    def feed_posts(self, params=None):
        endpoint = "/v1/feed/post/"
        params = self._merge_params(params, {
            "limit"         : "5",
            "offset"        : None,
            "comments_limit": "2",
        })
        if "only_allowed" not in params and self.extractor.only_allowed:
            params["only_allowed"] = "true"
        if "only_bought" not in params and self.extractor.only_bought:
            params["only_bought"] = "true"
        return self._pagination(endpoint, params, key="posts")

    def user(self, username):
        endpoint = "/v1/blog/" + username
        user = self._call(endpoint)
        user["id"] = user["owner"]["id"]
        return user

    def user_subscriptions(self, params=None):
        endpoint = "/v1/user/subscriptions"
        params = self._merge_params(params, {
            "limit"      : "30",
            "with_follow": "true",
            "offset"     : None,
        })
        return self._pagination_users(endpoint, params)

    def _merge_params(self, params_web, params_api):
        if params_web:
            web_to_api = {
                "isOnlyAllowedPosts": "is_only_allowed",
                "postsTagsIds"      : "tags_ids",
                "postsFrom"         : "from_ts",
                "postsTo"           : "to_ts",
            }
            for name, value in params_web.items():
                name = web_to_api.get(name, name)
                params_api[name] = value
        return params_api

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

    def _pagination(self, endpoint, params, transform=None, key=None):
        if "is_only_allowed" not in params and self.extractor.only_allowed:
            params["only_allowed"] = "true"
            params["is_only_allowed"] = "true"

        while True:
            data = self._call(endpoint, params)

            if transform:
                yield from transform(data["data"])
            elif key:
                yield from data["data"][key]
            else:
                yield from data["data"]

            extra = data["extra"]
            if extra.get("isLast"):
                return
            offset = extra.get("offset")
            if not offset:
                return
            params["offset"] = offset

    def _pagination_users(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            yield from data["data"]

            offset = data["offset"] + data["limit"]
            if offset > data["total"]:
                return
            params["offset"] = offset

    def dialog(self, dialog_id):
        endpoint = "/v1/dialog/{}".format(dialog_id)
        return self._call(endpoint)

    def dialog_messages(self, dialog_id, limit=300, offset=None):
        endpoint = "/v1/dialog/{}/message/".format(dialog_id)
        params = {
            "limit": limit,
            "reverse": "true",
            "offset": offset,
        }
        return self._pagination_dialog(endpoint, params)

    def _pagination_dialog(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            yield from data["data"]

            try:
                extra = data["extra"]
                if extra.get("isLast"):
                    break
                params["offset"] = offset = extra["offset"]
                if not offset:
                    break
            except Exception:
                break
