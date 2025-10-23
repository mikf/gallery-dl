# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.boosty.to/"""

from .common import Extractor, Message
from .. import text, util
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
        self.api = self.utils().BoostyAPI(self)

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
            post["date"] = self.parse_timestamp(post["createdAt"])

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

        if signed_query := post.get("signedQuery"):
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
    pattern = rf"{BASE_PATTERN}/([^/?#]+)(?:\?([^#]+))?$"
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
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/media/([^/?#]+)(?:\?([^#]+))?"
    example = "https://boosty.to/USER/media/all"

    def posts(self):
        user, media, query = self.groups
        params = text.parse_query(query)
        self._user = self.api.user(user)
        return self.api.blog_media_album(user, media, params)


class BoostyFeedExtractor(BoostyExtractor):
    """Extractor for your boosty.to subscription feed"""
    subcategory = "feed"
    pattern = rf"{BASE_PATTERN}/(?:\?([^#]+))?(?:$|#)"
    example = "https://boosty.to/"

    def posts(self):
        params = text.parse_query(self.groups[0])
        return self.api.feed_posts(params)


class BoostyPostExtractor(BoostyExtractor):
    """Extractor for boosty.to posts"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/posts/([0-9a-f-]+)"
    example = "https://boosty.to/USER/posts/01234567-89ab-cdef-0123-456789abcd"

    def posts(self):
        user, post_id = self.groups
        if self._user is None:
            self._user = self.api.user(user)
        return (self.api.post(user, post_id),)


class BoostyFollowingExtractor(BoostyExtractor):
    """Extractor for your boosty.to subscribed users"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/app/settings/subscriptions"
    example = "https://boosty.to/app/settings/subscriptions"

    def items(self):
        for user in self.api.user_subscriptions():
            url = f"{self.root}/{user['blog']['blogUrl']}"
            user["_extractor"] = BoostyUserExtractor
            yield Message.Queue, url, user


class BoostyDirectMessagesExtractor(BoostyExtractor):
    """Extractor for boosty.to direct messages"""
    subcategory = "direct-messages"
    directory_fmt = ("{category}", "{user[blogUrl]} ({user[id]})",
                     "Direct Messages")
    pattern = rf"{BASE_PATTERN}/app/messages/?\?dialogId=(\d+)"
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
