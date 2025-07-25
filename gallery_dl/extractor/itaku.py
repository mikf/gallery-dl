# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://itaku.ee/"""

from .common import Extractor, Message, Dispatch
from ..cache import memcache
from .. import text

BASE_PATTERN = r"(?:https?://)?itaku\.ee"
USER_PATTERN = BASE_PATTERN + r"/profile/([^/?#]+)"


class ItakuExtractor(Extractor):
    """Base class for itaku extractors"""
    category = "itaku"
    root = "https://itaku.ee"
    directory_fmt = ("{category}", "{owner_username}")
    filename_fmt = ("{id}{title:? //}.{extension}")
    archive_fmt = "{id}"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.api = ItakuAPI(self)
        self.videos = self.config("videos", True)

    def items(self):
        for post in self.posts():

            post["date"] = text.parse_datetime(
                post["date_added"], "%Y-%m-%dT%H:%M:%S.%fZ")
            for category, tags in post.pop("categorized_tags").items():
                post["tags_" + category.lower()] = [t["name"] for t in tags]
            post["tags"] = [t["name"] for t in post["tags"]]

            sections = []
            for s in post["sections"]:
                if group := s["group"]:
                    sections.append(group["title"] + "/" + s["title"])
                else:
                    sections.append(s["title"])
            post["sections"] = sections

            if post["video"] and self.videos:
                url = post["video"]["video"]
            else:
                url = post["image"]

            yield Message.Directory, post
            yield Message.Url, url, text.nameext_from_url(url, post)

    def items_user(self, users):
        base = f"{self.root}/profile/"
        for user in users:
            url = f"{base}{user['owner_username']}"
            user["_extractor"] = ItakuUserExtractor
            yield Message.Queue, url, user


class ItakuGalleryExtractor(ItakuExtractor):
    """Extractor for posts from an itaku user gallery"""
    subcategory = "gallery"
    pattern = USER_PATTERN + r"/gallery(?:/(\d+))?"
    example = "https://itaku.ee/profile/USER/gallery"

    def posts(self):
        return self.api.galleries_images(*self.groups)


class ItakuStarsExtractor(ItakuExtractor):
    subcategory = "stars"
    pattern = USER_PATTERN + r"/stars(?:/(\d+))?"
    example = "https://itaku.ee/profile/USER/stars"

    def posts(self):
        return self.api.galleries_images_starred(*self.groups)


class ItakuFollowingExtractor(ItakuExtractor):
    subcategory = "following"
    pattern = USER_PATTERN + r"/following"
    example = "https://itaku.ee/profile/USER/following"

    def items(self):
        return self.items_user(self.api.user_following(self.groups[0]))


class ItakuFollowersExtractor(ItakuExtractor):
    subcategory = "followers"
    pattern = USER_PATTERN + r"/followers"
    example = "https://itaku.ee/profile/USER/followers"

    def items(self):
        return self.items_user(self.api.user_followers(self.groups[0]))


class ItakuUserExtractor(Dispatch, ItakuExtractor):
    """Extractor for itaku user profiles"""
    pattern = USER_PATTERN + r"/?(?:$|\?|#)"
    example = "https://itaku.ee/profile/USER"

    def items(self):
        base = f"{self.root}/profile/{self.groups[0]}/"
        return self._dispatch_extractors((
            (ItakuGalleryExtractor  , base + "gallery"),
            (ItakuFollowersExtractor, base + "followers"),
            (ItakuFollowingExtractor, base + "following"),
            (ItakuStarsExtractor    , base + "stara"),
        ), ("gallery",))


class ItakuImageExtractor(ItakuExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/images/(\d+)"
    example = "https://itaku.ee/images/12345"

    def posts(self):
        return (self.api.image(self.groups[0]),)


class ItakuSearchExtractor(ItakuExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/home/images/?\?([^#]+)"
    example = "https://itaku.ee/home/images?tags=SEARCH"

    def posts(self):
        params = text.parse_query_list(
            self.groups[0], {"tags", "maturity_rating"})
        return self.api.search_images(params)


class ItakuAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
        }

    def search_images(self, params):
        endpoint = "/galleries/images/"
        required_tags = []
        negative_tags = []
        optional_tags = []

        for tag in params.pop("tags", None) or ():
            if not tag:
                pass
            elif tag[0] == "-":
                negative_tags.append(tag[1:])
            elif tag[0] == "~":
                optional_tags.append(tag[1:])
            else:
                required_tags.append(tag)

        api_params = {
            "required_tags": required_tags,
            "negative_tags": negative_tags,
            "optional_tags": optional_tags,
            "date_range": "",
            "maturity_rating": ("SFW", "Questionable", "NSFW"),
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "30",
            "visibility": ("PUBLIC", "PROFILE_ONLY"),
        }
        api_params.update(params)
        return self._pagination(endpoint, api_params, self.image)

    def galleries_images(self, username, section=None):
        endpoint = "/galleries/images/"
        params = {
            "cursor"    : None,
            "owner"     : self.user(username)["owner"],
            "sections"  : section,
            "date_range": "",
            "maturity_rating": ("SFW", "Questionable", "NSFW"),
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "30",
            "visibility": ("PUBLIC", "PROFILE_ONLY"),
        }
        return self._pagination(endpoint, params, self.image)

    def galleries_images_starred(self, username, section=None):
        endpoint = "/galleries/images/user_starred_imgs/"
        params = {
            "cursor"    : None,
            "stars_of"  : self.user(username)["owner"],
            "sections"  : section,
            "date_range": "",
            "ordering"  : "-date_added",
            "maturity_rating": ("SFW", "Questionable", "NSFW"),
            "page"      : "1",
            "page_size" : "30",
            "visibility": ("PUBLIC", "PROFILE_ONLY"),
        }
        return self._pagination(endpoint, params, self.image)

    def image(self, image_id):
        endpoint = f"/galleries/images/{image_id}/"
        return self._call(endpoint)

    def user_following(self, username):
        endpoint = "/user_profiles/"
        params = {
            "cursor"    : None,
            "followed_by": self.user(username)["owner"],
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "50",
            "sfw_only"  : "false",
        }
        return self._pagination(endpoint, params)

    def user_followers(self, username):
        endpoint = "/user_profiles/"
        params = {
            "cursor"    : None,
            "followers_of": self.user(username)["owner"],
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "50",
            "sfw_only"  : "false",
        }
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def user(self, username):
        return self._call(f"/user_profiles/{username}/")

    def _call(self, endpoint, params=None):
        if not endpoint.startswith("http"):
            endpoint = self.root + endpoint
        return self.extractor.request_json(
            endpoint, params=params, headers=self.headers)

    def _pagination(self, endpoint, params, extend=None):
        data = self._call(endpoint, params)

        while True:
            if extend is None:
                yield from data["results"]
            else:
                for result in data["results"]:
                    yield extend(result["id"])

            url_next = data["links"].get("next")
            if not url_next:
                return

            data = self._call(url_next)
