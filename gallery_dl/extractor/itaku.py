# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://itaku.ee/"""

from .common import Extractor, Message, Dispatch
from .. import text, util

BASE_PATTERN = r"(?:https?://)?itaku\.ee"
USER_PATTERN = rf"{BASE_PATTERN}/profile/([^/?#]+)"


class ItakuExtractor(Extractor):
    """Base class for itaku extractors"""
    category = "itaku"
    root = "https://itaku.ee"
    directory_fmt = ("{category}", "{owner_username}")
    filename_fmt = ("{id}{title:? //}.{extension}")
    archive_fmt = "{id}"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.api = self.utils().ItakuAPI(self)
        self.videos = self.config("videos", True)

    def items(self):
        if images := self.images():
            for image in images:
                image["date"] = self.parse_datetime_iso(image["date_added"])
                for category, tags in image.pop("categorized_tags").items():
                    image[f"tags_{category.lower()}"] = [
                        t["name"] for t in tags]
                image["tags"] = [t["name"] for t in image["tags"]]

                sections = []
                for s in image["sections"]:
                    if group := s["group"]:
                        sections.append(f"{group['title']}/{s['title']}")
                    else:
                        sections.append(s["title"])
                image["sections"] = sections

                if self.videos and image["video"]:
                    url = image["video"]["video"]
                else:
                    url = image["image"]

                yield Message.Directory, image
                yield Message.Url, url, text.nameext_from_url(url, image)
            return

        if posts := self.posts():
            for post in posts:
                images = post.pop("gallery_images") or ()
                post["count"] = len(images)
                post["date"] = self.parse_datetime_iso(post["date_added"])
                post["tags"] = [t["name"] for t in post["tags"]]

                yield Message.Directory, post
                for post["num"], image in enumerate(images, 1):
                    post["file"] = image
                    image["date"] = self.parse_datetime_iso(
                        image["date_added"])

                    url = image["image"]
                    yield Message.Url, url, text.nameext_from_url(url, post)
            return

        if users := self.users():
            base = f"{self.root}/profile/"
            for user in users:
                url = f"{base}{user['owner_username']}"
                user["_extractor"] = ItakuUserExtractor
                yield Message.Queue, url, user
            return

    images = posts = users = util.noop


class ItakuGalleryExtractor(ItakuExtractor):
    """Extractor for an itaku user's gallery"""
    subcategory = "gallery"
    pattern = rf"{USER_PATTERN}/gallery(?:/(\d+))?"
    example = "https://itaku.ee/profile/USER/gallery"

    def images(self):
        user, section = self.groups
        return self.api.galleries_images({
            "owner"   : self.api.user_id(user),
            "sections": section,
        })


class ItakuPostsExtractor(ItakuExtractor):
    """Extractor for an itaku user's posts"""
    subcategory = "posts"
    directory_fmt = ("{category}", "{owner_username}", "Posts",
                     "{id}{title:? //}")
    filename_fmt = "{file[id]}{file[title]:? //}.{extension}"
    archive_fmt = "{id}_{file[id]}"
    pattern = rf"{USER_PATTERN}/posts(?:/(\d+))?"
    example = "https://itaku.ee/profile/USER/posts"

    def posts(self):
        user, folder = self.groups
        return self.api.posts({
            "owner"  : self.api.user_id(user),
            "folders": folder,
        })


class ItakuStarsExtractor(ItakuExtractor):
    """Extractor for an itaku user's starred images"""
    subcategory = "stars"
    pattern = rf"{USER_PATTERN}/stars(?:/(\d+))?"
    example = "https://itaku.ee/profile/USER/stars"

    def images(self):
        user, section = self.groups
        return self.api.galleries_images({
            "stars_of": self.api.user_id(user),
            "sections": section,
            "ordering": "-like_date",
        }, "/user_starred_imgs")


class ItakuFollowingExtractor(ItakuExtractor):
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/following"
    example = "https://itaku.ee/profile/USER/following"

    def users(self):
        return self.api.user_profiles({
            "followed_by": self.api.user_id(self.groups[0]),
        })


class ItakuFollowersExtractor(ItakuExtractor):
    subcategory = "followers"
    pattern = rf"{USER_PATTERN}/followers"
    example = "https://itaku.ee/profile/USER/followers"

    def users(self):
        return self.api.user_profiles({
            "followers_of": self.api.user_id(self.groups[0]),
        })


class ItakuBookmarksExtractor(ItakuExtractor):
    """Extractor for an itaku bookmarks folder"""
    subcategory = "bookmarks"
    pattern = rf"{USER_PATTERN}/bookmarks/(image|user)/(\d+)"
    example = "https://itaku.ee/profile/USER/bookmarks/image/12345"

    def _init(self):
        if self.groups[1] == "user":
            self.images = util.noop
        ItakuExtractor._init(self)

    def images(self):
        return self.api.galleries_images({
            "bookmark_folder": self.groups[2],
        })

    def users(self):
        return self.api.user_profiles({
            "bookmark_folder": self.groups[2],
        })


class ItakuUserExtractor(Dispatch, ItakuExtractor):
    """Extractor for itaku user profiles"""
    pattern = rf"{USER_PATTERN}/?(?:$|\?|#)"
    example = "https://itaku.ee/profile/USER"

    def items(self):
        base = f"{self.root}/profile/{self.groups[0]}/"
        return self._dispatch_extractors((
            (ItakuGalleryExtractor  , base + "gallery"),
            (ItakuPostsExtractor    , base + "posts"),
            (ItakuFollowersExtractor, base + "followers"),
            (ItakuFollowingExtractor, base + "following"),
            (ItakuStarsExtractor    , base + "stars"),
        ), ("gallery",))


class ItakuImageExtractor(ItakuExtractor):
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/images/(\d+)"
    example = "https://itaku.ee/images/12345"

    def images(self):
        return (self.api.image(self.groups[0]),)


class ItakuPostExtractor(ItakuExtractor):
    subcategory = "post"
    directory_fmt = ("{category}", "{owner_username}", "Posts",
                     "{id}{title:? //}")
    filename_fmt = "{file[id]}{file[title]:? //}.{extension}"
    archive_fmt = "{id}_{file[id]}"
    pattern = rf"{BASE_PATTERN}/posts/(\d+)"
    example = "https://itaku.ee/posts/12345"

    def posts(self):
        return (self.api.post(self.groups[0]),)


class ItakuSearchExtractor(ItakuExtractor):
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/home/images/?\?([^#]+)"
    example = "https://itaku.ee/home/images?tags=SEARCH"

    def images(self):
        required_tags = []
        negative_tags = []
        optional_tags = []

        params = text.parse_query_list(
            self.groups[0], {"tags", "maturity_rating"})
        if tags := params.pop("tags", None):
            for tag in tags:
                if not tag:
                    pass
                elif tag[0] == "-":
                    negative_tags.append(tag[1:])
                elif tag[0] == "~":
                    optional_tags.append(tag[1:])
                else:
                    required_tags.append(tag)

        return self.api.galleries_images({
            "required_tags": required_tags,
            "negative_tags": negative_tags,
            "optional_tags": optional_tags,
        })
