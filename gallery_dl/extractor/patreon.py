# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.patreon.com/"""

from .common import Extractor, Message
from .. import text
from ..cache import memcache


class PatreonExtractor(Extractor):
    """Base class for patreon extractors"""
    category = "patreon"
    root = "https://www.patreon.com"
    directory_fmt = ("{category}", "{creator[full_name]}")
    filename_fmt = "{id}_{title}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    _warning = True

    def items(self):
        yield Message.Version, 1

        if self._warning:
            if "session_id" not in self.session.cookies:
                self.log.warning("no 'session_id' cookie set")
            PatreonExtractor._warning = False

        for post in self.posts():
            yield Message.Directory, post

            post["num"] = 0
            content = post.get("content")
            postfile = post.get("post_file")

            for url in text.extract_iter(content or "", 'src="', '"'):
                post["num"] += 1
                yield Message.Url, url, text.nameext_from_url(url, post)

            if postfile:
                post["num"] += 1
                url = postfile["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

            for attachment in post["attachments"]:
                post["num"] += 1
                url = attachment["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, url):
        headers = {"Referer": self.root}
        params = {}
        empty = []

        while url:
            posts = self.request(url, headers=headers, params=params).json()

            if "included" not in posts:
                return

            # collect attachments
            attachments = {}
            for inc in posts["included"]:
                if inc["type"] == "attachment":
                    attachments[inc["id"]] = inc["attributes"]

            # update posts
            for post in posts["data"]:
                attr = post["attributes"]
                attr["id"] = text.parse_int(post["id"])
                attr["date"] = text.parse_datetime(
                    attr["published_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                attr["creator"] = self._user(
                    post["relationships"]["user"]["links"]["related"])

                # add attachments to post attributes
                files = post["relationships"].get("attachments")
                if files:
                    attr["attachments"] = [
                        attachments[f["id"]]
                        for f in files["data"]
                    ]
                else:
                    attr["attachments"] = empty

                yield attr

            if "links" not in posts:
                return
            url = posts["links"].get("next")

    @memcache(keyarg=1)
    def _user(self, url):
        user = self.request(url).json()["data"]
        attr = user["attributes"]
        attr["id"] = user["id"]
        attr["date"] = text.parse_datetime(
            attr["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
        return attr

    @staticmethod
    def _build_url(endpoint, query):
        return (
            "https://www.patreon.com/api/" + endpoint +

            "?include=user,attachments,user_defined_tags,campaign,poll.choices"
            ",poll.current_user_responses.user,poll.current_user_responses.cho"
            "ice,poll.current_user_responses.poll,access_rules.tier.null"

            "&fields[post]=change_visibility_at,comment_count,content,current_"
            "user_can_delete,current_user_can_view,current_user_has_liked,embe"
            "d,image,is_paid,like_count,min_cents_pledged_to_view,post_file,pu"
            "blished_at,patron_count,patreon_url,post_type,pledge_url,thumbnai"
            "l_url,teaser_text,title,upgrade_url,url,was_posted_by_campaign_ow"
            "ner"
            "&fields[user]=image_url,full_name,url"
            "&fields[campaign]=avatar_photo_url,earnings_visibility,is_nsfw,is"
            "_monthly,name,url"
            "&fields[access_rule]=access_rule_type,amount_cents" + query +

            "&json-api-use-default-includes=false"
            "&json-api-version=1.0"
        )


class PatreonCreatorExtractor(PatreonExtractor):
    """Extractor for a creator's works"""
    subcategory = "creator"
    pattern = (r"(?:https?://)?(?:www\.)?patreon\.com"
               r"/(?!(?:home|join|login|signup)(?:$|[/?&#]))([^/?&#]+)/?")
    test = ("https://www.patreon.com/koveliana", {
        "range": "1-25",
        "count": ">= 25",
        "keyword": {
            "attachments": list,
            "comment_count": int,
            "content": str,
            "creator": dict,
            "date": "type:datetime",
            "id": int,
            "like_count": int,
            "post_type": str,
            "published_at": str,
            "title": str,
        },
    })

    def __init__(self, match):
        PatreonExtractor.__init__(self, match)
        self.creator = match.group(1).lower()

    def posts(self):
        url = "{}/{}".format(self.root, self.creator)
        page = self.request(url).text
        campaign_id = text.extract(page, "/campaign/", "/")[0]

        url = self._build_url("posts", (
            "&sort=-published_at"
            "&filter[is_draft]=false"
            "&filter[contains_exclusive_posts]=true"
            "&filter[campaign_id]=" + campaign_id
        ))
        return self._pagination(url)


class PatreonUserExtractor(PatreonExtractor):
    """Extractor for media from creators supported by you"""
    subcategory = "user"
    pattern = r"(?:https?://)?(?:www\.)?patreon\.com/home$"
    test = ("https://www.patreon.com/home",)

    def posts(self):
        url = self._build_url("stream", (
            "&page[cursor]=null"
            "&filter[is_following]=true"
        ))
        return self._pagination(url)
