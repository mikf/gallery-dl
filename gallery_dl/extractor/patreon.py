# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.patreon.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import memcache
import collections
import itertools
import json


class PatreonExtractor(Extractor):
    """Base class for patreon extractors"""
    category = "patreon"
    root = "https://www.patreon.com"
    directory_fmt = ("{category}", "{creator[full_name]}")
    filename_fmt = "{id}_{title}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    browser = "firefox"
    _warning = True

    def items(self):
        yield Message.Version, 1

        if self._warning:
            if "session_id" not in self.session.cookies:
                self.log.warning("no 'session_id' cookie set")
            PatreonExtractor._warning = False

        for post in self.posts():

            if not post.get("current_user_can_view", True):
                self.log.warning("Not allowed to view post %s", post["id"])
                continue
            post["num"] = 0
            hashes = set()

            yield Message.Directory, post
            for kind, url, name in itertools.chain(
                self._images(post),
                self._attachments(post),
                self._postfile(post),
                self._content(post),
            ):
                fhash = self._filehash(url)
                if fhash not in hashes or not fhash:
                    hashes.add(fhash)
                    post["hash"] = fhash
                    post["type"] = kind
                    post["num"] += 1
                    yield Message.Url, url, text.nameext_from_url(name, post)
                else:
                    self.log.debug("skipping %s (%s %s)", url, fhash, kind)

    @staticmethod
    def _postfile(post):
        postfile = post.get("post_file")
        if postfile:
            return (("postfile", postfile["url"], postfile["name"]),)
        return ()

    def _images(self, post):
        for image in post["images"]:
            url = image.get("download_url")
            if url:
                name = image.get("file_name") or self._filename(url) or url
                yield "image", url, name

    def _attachments(self, post):
        for attachment in post["attachments"]:
            url = self.request(
                attachment["url"], method="HEAD",
                allow_redirects=False, fatal=False,
            ).headers.get("Location")

            if url:
                yield "attachment", url, attachment["name"]

    @staticmethod
    def _content(post):
        content = post.get("content")
        if content:
            for img in text.extract_iter(
                    content, '<img data-media-id="', '>'):
                url = text.extract(img, 'src="', '"')[0]
                if url:
                    yield "content", url, url

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, url):
        headers = {"Referer": self.root}

        while url:
            url = text.ensure_http_scheme(url)
            posts = self.request(url, headers=headers).json()

            if "included" in posts:
                included = self._transform(posts["included"])
                for post in posts["data"]:
                    yield self._process(post, included)

            if "links" not in posts:
                return
            url = posts["links"].get("next")

    def _process(self, post, included):
        """Process and extend a 'post' object"""
        attr = post["attributes"]
        attr["id"] = text.parse_int(post["id"])

        if post.get("current_user_can_view", True):
            attr["images"] = self._files(post, included, "images")
            attr["attachments"] = self._files(post, included, "attachments")
            attr["date"] = text.parse_datetime(
                attr["published_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
            user = post["relationships"]["user"]
            attr["creator"] = (
                self._user(user["links"]["related"]) or
                included["user"][user["data"]["id"]])

        return attr

    @staticmethod
    def _transform(included):
        """Transform 'included' into an easier to handle format"""
        result = collections.defaultdict(dict)
        for inc in included:
            result[inc["type"]][inc["id"]] = inc["attributes"]
        return result

    @staticmethod
    def _files(post, included, key):
        """Build a list of files"""
        files = post["relationships"].get(key)
        if files and files.get("data"):
            return [
                included[file["type"]][file["id"]]
                for file in files["data"]
            ]
        return []

    @memcache(keyarg=1)
    def _user(self, url):
        """Fetch user information"""
        response = self.request(url, fatal=False)
        if response.status_code >= 400:
            return None
        user = response.json()["data"]
        attr = user["attributes"]
        attr["id"] = user["id"]
        attr["date"] = text.parse_datetime(
            attr["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
        return attr

    def _filename(self, url):
        """Fetch filename from an URL's Content-Disposition header"""
        response = self.request(url, method="HEAD", fatal=False)
        cd = response.headers.get("Content-Disposition")
        return text.extract(cd, 'filename="', '"')[0]

    @staticmethod
    def _filehash(url):
        """Extract MD5 hash from a download URL"""
        parts = url.partition("?")[0].split("/")
        parts.reverse()

        for part in parts:
            if len(part) == 32:
                return part
        return ""

    @staticmethod
    def _build_url(endpoint, query):
        return (
            "https://www.patreon.com/api/" + endpoint +

            "?include=user,images,attachments,user_defined_tags,campaign,poll."
            "choices,poll.current_user_responses.user,poll.current_user_respon"
            "ses.choice,poll.current_user_responses.poll,access_rules.tier.nul"
            "l"

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
               r"/(?!(?:home|join|posts|login|signup)(?:$|[/?#]))"
               r"([^/?#]+)(?:/posts)?/?(?:\?([^#]+))?")
    test = (
        ("https://www.patreon.com/koveliana", {
            "range": "1-25",
            "count": ">= 25",
            "keyword": {
                "attachments"  : list,
                "comment_count": int,
                "content"      : str,
                "creator"      : dict,
                "date"         : "type:datetime",
                "id"           : int,
                "images"       : list,
                "like_count"   : int,
                "post_type"    : str,
                "published_at" : str,
                "title"        : str,
            },
        }),
        ("https://www.patreon.com/koveliana/posts?filters[month]=2020-3", {
            "count": 1,
            "keyword": {"date": "dt:2020-03-30 21:21:44"},
        }),
        ("https://www.patreon.com/kovelianot", {
            "exception": exception.NotFoundError,
        }),
        ("https://www.patreon.com/user?u=2931440"),
        ("https://www.patreon.com/user/posts/?u=2931440"),
    )

    def __init__(self, match):
        PatreonExtractor.__init__(self, match)
        self.creator, self.query = match.groups()

    def posts(self):
        query = text.parse_query(self.query)

        creator_id = query.get("u")
        if creator_id:
            url = "{}/user/posts?u={}".format(self.root, creator_id)
        else:
            url = "{}/{}/posts".format(self.root, self.creator)

        page = self.request(url, notfound="creator").text
        campaign_id = text.extract(page, "/campaign/", "/")[0]
        if not campaign_id:
            raise exception.NotFoundError("creator")

        filters = "".join(
            "&filter[{}={}".format(key[8:], text.escape(value))
            for key, value in query.items()
            if key.startswith("filters[")
        )

        url = self._build_url("posts", (
            "&sort=" + query.get("sort", "-published_at") +
            "&filter[is_draft]=false"
            "&filter[contains_exclusive_posts]=true"
            "&filter[campaign_id]=" + campaign_id + filters
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


class PatreonPostExtractor(PatreonExtractor):
    """Extractor for media from a single post"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?patreon\.com/posts/([^/?#]+)"
    test = (
        # postfile + attachments
        ("https://www.patreon.com/posts/precious-metal-23563293", {
            "count": 4,
        }),
        # postfile + content
        ("https://www.patreon.com/posts/19987002", {
            "count": 4,
        }),
        ("https://www.patreon.com/posts/not-found-123", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        PatreonExtractor.__init__(self, match)
        self.slug = match.group(1)

    def posts(self):
        url = "{}/posts/{}".format(self.root, self.slug)
        page = self.request(url, notfound="post").text
        data = text.extract(page, "window.patreon.bootstrap,", "\n});")[0]
        post = json.loads(data + "}")["post"]

        included = self._transform(post["included"])
        return (self._process(post["data"], included),)
