# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.artstation.com/"""

from .common import Extractor, Message
from .. import text, util, exception
import random
import string


class ArtstationExtractor(Extractor):
    """Base class for artstation extractors"""
    category = "artstation"
    directory_fmt = ["{category}", "{username}"]
    filename_fmt = "{category}_{id}_{asset[id]}_{title}.{extension}"
    archive_fmt = "{asset[id]}"
    root = "https://www.artstation.com"
    per_page = 50

    def __init__(self, match=None):
        Extractor.__init__(self)
        self.user = match.group(1) if match else None
        self.external = self.config("external", False)

    def items(self):
        userinfo = None
        yield Message.Version, 1

        for project_id in self.projects():
            for asset in self.get_project_assets(project_id):
                if not userinfo:
                    userinfo = self.get_user_info(
                        self.user or asset["user"]["username"])
                    yield Message.Directory, userinfo

                adict = asset["asset"]
                asset["userinfo"] = userinfo

                if adict["has_image"]:
                    url = adict["image_url"]
                    text.nameext_from_url(url, asset)
                    yield Message.Url, self._no_cache(url), asset

                if adict["has_embedded_player"] and self.external:
                    url = text.extract(adict["player_embedded"], '"', '"')[0]
                    yield Message.Queue, url, asset

    def projects(self):
        """Return an iterable containing all relevant project IDs"""

    def get_project_assets(self, project_id):
        """Return all assets associated with 'project_id'"""
        url = "{}/projects/{}.json".format(self.root, project_id)
        data = self.request(url).json()

        data["title"] = text.unescape(data["title"])
        data["description"] = text.unescape(text.remove_html(
            data["description"]))

        assets = data["assets"]
        del data["assets"]

        for asset in assets:
            data["asset"] = asset
            yield data

    def get_user_info(self, username):
        """Return metadata for a specific user"""
        url = "{}/users/{}/quick.json".format(self.root, username.lower())
        response = self.request(url, fatal=False, allow_empty=True)
        if response.status_code == 404:
            raise exception.NotFoundError("user")
        return response.json()

    def _pagination(self, url):
        params = {"page": 1}
        while True:
            projects = self.request(url, params=params).json()["data"]
            for project in projects:
                yield project["hash_id"]
            if len(projects) < self.per_page:
                return
            params["page"] += 1

    @staticmethod
    def _no_cache(url, alphabet=(string.digits + string.ascii_letters)):
        """Cause a cache miss to prevent Cloudflare 'optimizations'

        Cloudflare's 'Polish' optimization strips image metadata and may even
        recompress an image as lossy JPEG. This can be prevented by causing
        a cache miss when requesting an image by adding a random dummy query
        parameter.

        Ref:
        https://github.com/r888888888/danbooru/issues/3528
        https://danbooru.donmai.us/forum_topics/14952
        """
        param = "gallerydl_no_cache=" + util.bencode(
            random.getrandbits(64), alphabet)
        sep = "&" if "?" in url else "?"
        return url + sep + param


class ArtstationUserExtractor(ArtstationExtractor):
    """Extractor for all projects of an artstation user"""
    subcategory = "user"
    pattern = [r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/(?!artwork|projects)([^/?&#]+)/?$",
               r"(?:https?://)?((?!www)\w+)\.artstation\.com"
               r"(?:/(?:projects/?)?)?$"]
    test = [
        ("https://www.artstation.com/gaerikim/", {
            "pattern": r"https://\w+\.artstation\.com/p/assets"
                       r"/images/images/\d+/\d+/\d+/large/[^/]+",
            "count": ">= 6",
        }),
        ("https://gaerikim.artstation.com/", None),
        ("https://gaerikim.artstation.com/projects/", None),
    ]

    def projects(self):
        url = "{}/users/{}/projects.json".format(self.root, self.user)
        return self._pagination(url)


class ArtstationLikesExtractor(ArtstationExtractor):
    """Extractor for liked projects of an artstation user"""
    subcategory = "likes"
    directory_fmt = ["{category}", "{username}", "Likes"]
    archive_fmt = "f_{userinfo[id]}_{asset[id]}"
    pattern = [r"(?:https?://)?(?:www\.)?artstation\.com"
               r"/(?!artwork|projects)([^/?&#]+)/likes/?"]
    test = [
        ("https://www.artstation.com/dcchris/likes", {
            "count": ">= 3",
        }),
        # no likes
        ("https://www.artstation.com/sungchoi/likes", {
            "count": 0,
        }),
    ]

    def projects(self):
        url = "{}/users/{}/likes.json".format(self.root, self.user)
        return self._pagination(url)


class ArtstationImageExtractor(ArtstationExtractor):
    """Extractor for images from a single artstation project"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:\w+\.)?artstation\.com"
               r"/(?:artwork|projects)/(\w+)"]
    test = [
        ("https://www.artstation.com/artwork/LQVJr", {
            "pattern": r"https?://\w+\.artstation\.com/p/assets"
                       r"/images/images/008/760/279/large/.+",
            "content": "1f645ce7634e44675ebde8f6b634d36db0617d3c",
            # SHA1 hash without _no_cache()
            # "content": "2e8aaf6400aeff2345274f45e90b6ed3f2a0d946",
        }),
        # multiple images per project
        ("https://www.artstation.com/artwork/Db3dy", {
            "count": 4,
        }),
        # different URL pattern
        ("https://sungchoi.artstation.com/projects/LQVJr", None),
    ]

    def __init__(self, match):
        ArtstationExtractor.__init__(self)
        self.project_id = match.group(1)

    def projects(self):
        return (self.project_id,)
