# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://itaku.ee/"""

from .common import Extractor, Message
from ..cache import memcache
from .. import text

BASE_PATTERN = r"(?:https?://)?itaku\.ee"


class ItakuExtractor(Extractor):
    """Base class for itaku extractors"""
    category = "itaku"
    root = "https://itaku.ee"
    directory_fmt = ("{category}", "{owner_username}")
    filename_fmt = ("{id}{title:? //}.{extension}")
    archive_fmt = "{id}"
    request_interval = (0.5, 1.5)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = ItakuAPI(self)
        self.item = match.group(1)
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
                group = s["group"]
                if group:
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


class ItakuGalleryExtractor(ItakuExtractor):
    """Extractor for posts from an itaku user gallery"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/profile/([^/?#]+)/gallery"
    test = ("https://itaku.ee/profile/piku/gallery", {
        "pattern": r"https://d1wmr8tlk3viaj\.cloudfront\.net/gallery_imgs"
                   r"/[^/?#]+\.(jpg|png|gif)",
        "range": "1-10",
        "count": 10,
    })

    def posts(self):
        return self.api.galleries_images(self.item)


class ItakuImageExtractor(ItakuExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/images/(\d+)"
    test = (
        ("https://itaku.ee/images/100471", {
            "pattern": r"https://d1wmr8tlk3viaj\.cloudfront\.net/gallery_imgs"
                       r"/220504_oUNIAFT\.png",
            "count": 1,
            "keyword": {
                "already_pinned": None,
                "blacklisted": {
                    "blacklisted_tags": [],
                    "is_blacklisted": False
                },
                "can_reshare": True,
                "date": "dt:2022-05-05 19:21:17",
                "date_added": "2022-05-05T19:21:17.674148Z",
                "date_edited": "2022-05-25T14:37:46.220612Z",
                "description": "sketch from drawpile",
                "extension": "png",
                "filename": "220504_oUNIAFT",
                "hotness_score": float,
                "id": 100471,
                "image": "https://d1wmr8tlk3viaj.cloudfront.net/gallery_imgs"
                         "/220504_oUNIAFT.png",
                "image_xl": "https://d1wmr8tlk3viaj.cloudfront.net"
                            "/gallery_imgs/220504_oUNIAFT/xl.jpg",
                "liked_by_you": False,
                "maturity_rating": "SFW",
                "num_comments": int,
                "num_likes": int,
                "num_reshares": int,
                "obj_tags": 136446,
                "owner": 16775,
                "owner_avatar": "https://d1wmr8tlk3viaj.cloudfront.net"
                                "/profile_pics/av2022r_vKYVywc/sm.jpg",
                "owner_displayname": "Piku",
                "owner_username": "piku",
                "reshared_by_you": False,
                "sections": ["Fanart/Miku"],
                "tags": list,
                "tags_character": ["hatsune_miku"],
                "tags_copyright": ["vocaloid"],
                "tags_general"  : ["female", "green_eyes", "twintails",
                                   "green_hair", "gloves", "flag",
                                   "racing_miku"],
                "title": "Racing Miku 2022 Ver.",
                "too_mature": False,
                "uncompressed_filesize": "0.62",
                "video": None,
                "visibility": "PUBLIC",
            },
        }),
        # video
        ("https://itaku.ee/images/19465", {
            "pattern": r"https://d1wmr8tlk3viaj\.cloudfront\.net/gallery_vids"
                       r"/sleepy_af_OY5GHWw\.mp4",
        }),
    )

    def posts(self):
        return (self.api.image(self.item),)


class ItakuAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": extractor.root + "/",
        }

    def galleries_images(self, username, section=None):
        endpoint = "/galleries/images/"
        params = {
            "cursor"    : None,
            "owner"     : self.user(username)["owner"],
            "section"   : section,
            "date_range": "",
            "maturity_rating": ("SFW", "Questionable", "NSFW", "Extreme"),
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "30",
            "visibility": ("PUBLIC", "PROFILE_ONLY"),
        }
        return self._pagination(endpoint, params, self.image)

    def image(self, image_id):
        endpoint = "/galleries/images/{}/".format(image_id)
        return self._call(endpoint)

    @memcache(keyarg=1)
    def user(self, username):
        return self._call("/user_profiles/{}/".format(username))

    def _call(self, endpoint, params=None):
        if not endpoint.startswith("http"):
            endpoint = self.root + endpoint
        response = self.extractor.request(
            endpoint, params=params, headers=self.headers)
        return response.json()

    def _pagination(self, endpoint, params, extend):
        data = self._call(endpoint, params)

        while True:
            if extend:
                for result in data["results"]:
                    yield extend(result["id"])
            else:
                yield from data["results"]

            url_next = data["links"].get("next")
            if not url_next:
                return

            data = self._call(url_next)
