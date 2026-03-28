# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Lemmy instances"""

import re
from .common import BaseExtractor, Message
from .. import text

class LemmyExtractor(BaseExtractor):
    """Base class for lemmy extractors"""
    basecategory = "lemmy"
    directory_fmt = ("lemmy", "{instance}", "{subcategory}", "{type_id}")
    filename_fmt = "{creator}_{id}.{extension}"
    archive_fmt = "{id}"

    def _init(self):
        self.apiClient = LemmyAPIClient(self)
        self.instance = self.root.rpartition("://")[2]
        self.download_from_comments = True if self.config("comments", True) else False
        self.comment_url_pattern = BASE_PATTERN + r"/pictrs/image/(([a-zA-Z0-9-]+)\.[a-zA-Z0-9]+)"

    def items(self):
        base_data = {
            "type_id": self.type_id,
            # TODO: Posts could be made in a different instance. Should this really always be the instance of the original link?
            "instance": self.instance,
        }

        yield Message.Directory, "", base_data

        content = self.find_content()
        for content in content:
            content_url = content.get("url")
            if not content_url:
                continue
            content_id = content["id"]

            # Prepare image metadata
            data = {
                "id": content_id,
                "creator": content["creator"]
            }
            text.nameext_from_url(content_url, data)

            data.update(base_data)

            if content_url.startswith(self.root + "/pictrs/image/"):
                yield Message.Url, content_url, data
            else:
                yield Message.Queue, content_url, data

    def find_content(self):
        """Return an iterable containing all relevant content objects"""
        return ()

    def extract_from_posts(self, posts):
        urls = []
        for post in posts:
            # Extract image URL and ID
            content_url = post["post"].get("url")
            if content_url == None:
                continue
            post_id = post["post"]["id"]

            id_with_ext = content_url.rpartition("/")[2]
            urls.append({
                "id": id_with_ext.rpartition(".")[0],
                "url": content_url,
                "creator": post["creator"]["name"],
            })
        return urls

    def extract_from_comments(self, comments):
        urls = []
        for comment in comments:
            # Get comment text
            content = comment["comment"].get("content")
            if not content:
                continue
            url_matches = re.finditer(self.comment_url_pattern, content)
            if not url_matches:
                continue

            for url_match in url_matches:
                content_url = url_match.group(0)
                urls.append({
                    "id": url_match.groups()[4],
                    "url": content_url,
                    "creator": comment["creator"]["name"],
                })
        return urls

BASE_PATTERN = LemmyExtractor.update({
    "lemmynsfw.com": {
        "root": "https://lemmynsfw.com",
        "pattern": r"lemmynsfw\.com",
    },
    "lemmy.world": {
        "root": "https://lemmy.world",
        "pattern": r"lemmy\.world",
    },
})

class LemmyUserExtractor(LemmyExtractor):
    """Extractor lemmy user profiles"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/u/([a-zA-Z0-9]+(@[a-zA-Z0-9_.\-~]+.[a-zA-Z0-9]+)?)"

    def __init__(self, match):
        LemmyExtractor.__init__(self, match)
        self.type_id = self.groups[3]

    def find_content(self):
        content = self.extract_from_posts(self.apiClient.user_posts(self.type_id))
        if self.download_from_comments:
            content.extend(self.extract_from_comments(self.apiClient.user_comments(self.type_id)))
        return content

class LemmyCommunityExtractor(LemmyExtractor):
    """Extractor for lemmy communities"""
    subcategory = "community"
    pattern = BASE_PATTERN + r"/c/([a-zA-Z0-9]+)"

    def __init__(self, match):
        LemmyExtractor.__init__(self, match)
        self.type_id = self.groups[-1]

    def find_content(self):
        content = self.extract_from_posts(self.apiClient.community_posts(self.type_id))
        if self.download_from_comments:
            content.extend(self.extract_from_comments(self.apiClient.community_comments(self.type_id)))
        return content

class LemmyAPIClient:
    """Minimal interface for the Lemmy v19 API (API v3)"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api/v3"

    def user_posts(self, username):
        return self.extractor.cache(self._user_profile, username)["posts"]

    def user_comments(self, username):
        return self.extractor.cache(self._user_profile, username)["comments"]

    def _user_profile(self, username):
        endpoint = self.root + "/user"
        params = {
            "username": username,
            "sort": "New",
            "limit": 50,
        }
        return self._pagination(endpoint, params, ["posts", "comments"])

    def community_posts(self, community_name):
        """Get posts of the community"""
        endpoint = self.root + "/post/list"
        params = {
            "community_name": community_name,
            "sort": "New",
            "limit": 50,
        }
        return self._pagination(endpoint, params, ["posts"])["posts"]

    def community_comments(self, community_name):
        endpoint = self.root + "/comment/list"
        params = {
            "community_name": community_name,
            "sort": "New",
            "limit": 50,
        }
        return self._pagination(endpoint, params, ["comments"])["comments"]

    def _call(self, endpoint, params=None):
        try:
            return self.extractor.request(endpoint, params=params).json()
        except self.extractor.exc.HttpError:
            return None

    def _pagination(self, endpoint, params, entities):
        """Get posts of the user"""
        # Pagination is awkward in v3, v4 will return a 'page_cursor'
        # for the next page
        page_num = 1
        content = {item: [] for item in entities}

        while True:
            self.extractor.log.debug("Loading page %d", page_num)
            params["page"] = page_num
            page = self._call(endpoint, params)

            if not page:
                return content

            selected_entities = {item: page[item] for item in entities}

            if not any(selected_entities.values()):
                return content

            for entity_type, cur_entities in selected_entities.items():
                content[entity_type].extend(cur_entities)

            page_num += 1
