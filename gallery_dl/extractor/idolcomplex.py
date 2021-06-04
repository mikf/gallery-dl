# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://idol.sankakucomplex.com/"""

from .sankaku import SankakuExtractor
from .common import Message
from ..cache import cache
from .. import text, util, exception
import collections
import re


class IdolcomplexExtractor(SankakuExtractor):
    """Base class for idolcomplex extractors"""
    category = "idolcomplex"
    cookienames = ("login", "pass_hash")
    cookiedomain = "idol.sankakucomplex.com"
    root = "https://" + cookiedomain
    request_interval = 5.0

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.logged_in = True
        self.start_page = 1
        self.start_post = 0
        self.extags = self.config("tags", False)

    def items(self):
        self.login()
        data = self.metadata()

        for post_id in util.advance(self.post_ids(), self.start_post):
            post = self._parse_post(post_id)
            url = post["file_url"]
            post.update(data)
            text.nameext_from_url(url, post)
            yield Message.Directory, post
            yield Message.Url, url, post

    def skip(self, num):
        self.start_post += num
        return num

    def post_ids(self):
        """Return an iterable containing all relevant post ids"""

    def login(self):
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            cookies = self._login_impl(username, password)
            self._update_cookies(cookies)
        else:
            self.logged_in = False

    @cache(maxage=90*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/user/authenticate"
        data = {
            "url"           : "",
            "user[name]"    : username,
            "user[password]": password,
            "commit"        : "Login",
        }
        response = self.request(url, method="POST", data=data)

        if not response.history or response.url != self.root + "/user/home":
            raise exception.AuthenticationError()
        cookies = response.history[0].cookies
        return {c: cookies[c] for c in self.cookienames}

    def _parse_post(self, post_id):
        """Extract metadata of a single post"""
        url = self.root + "/post/show/" + post_id
        page = self.request(url, retries=10).text
        extr = text.extract

        tags   , pos = extr(page, "<title>", " | ")
        vavg   , pos = extr(page, "itemprop=ratingValue>", "<", pos)
        vcnt   , pos = extr(page, "itemprop=reviewCount>", "<", pos)
        _      , pos = extr(page, "Posted: <", "", pos)
        created, pos = extr(page, ' title="', '"', pos)
        rating = extr(page, "<li>Rating: ", "<", pos)[0]

        file_url, pos = extr(page, '<li>Original: <a href="', '"', pos)
        if file_url:
            width , pos = extr(page, '>', 'x', pos)
            height, pos = extr(page, '', ' ', pos)
        else:
            width , pos = extr(page, '<object width=', ' ', pos)
            height, pos = extr(page, 'height=', '>', pos)
            file_url = extr(page, '<embed src="', '"', pos)[0]

        data = {
            "id": text.parse_int(post_id),
            "md5": file_url.rpartition("/")[2].partition(".")[0],
            "tags": text.unescape(tags),
            "vote_average": text.parse_float(vavg),
            "vote_count": text.parse_int(vcnt),
            "created_at": created,
            "rating": (rating or "?")[0].lower(),
            "file_url": "https:" + text.unescape(file_url),
            "width": text.parse_int(width),
            "height": text.parse_int(height),
        }

        if self.extags:
            tags = collections.defaultdict(list)
            tags_html = text.extract(page, '<ul id=tag-sidebar>', '</ul>')[0]
            pattern = re.compile(r'tag-type-([^>]+)><a href="/\?tags=([^"]+)')
            for tag_type, tag_name in pattern.findall(tags_html or ""):
                tags[tag_type].append(text.unquote(tag_name))
            for key, value in tags.items():
                data["tags_" + key] = " ".join(value)

        return data


class IdolcomplexTagExtractor(IdolcomplexExtractor):
    """Extractor for images from idol.sankakucomplex.com by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = r"(?:https?://)?idol\.sankakucomplex\.com/\?([^#]*)"
    test = (
        ("https://idol.sankakucomplex.com/?tags=lyumos", {
            "count": 5,
            "range": "18-22",
            "pattern": r"https://is\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}"
                       r"/[^/]{32}\.\w+\?e=\d+&m=[^&#]+",
        }),
        ("https://idol.sankakucomplex.com/?tags=order:favcount", {
            "count": 5,
            "range": "18-22",
        }),
        ("https://idol.sankakucomplex.com"
         "/?tags=lyumos+wreath&page=3&next=694215"),
    )
    per_page = 20

    def __init__(self, match):
        IdolcomplexExtractor.__init__(self, match)
        query = text.parse_query(match.group(1))
        self.tags = text.unquote(query.get("tags", "").replace("+", " "))
        self.start_page = text.parse_int(query.get("page"), 1)
        self.next = text.parse_int(query.get("next"), 0)

    def skip(self, num):
        if self.next:
            self.start_post += num
        else:
            pages, posts = divmod(num, self.per_page)
            self.start_page += pages
            self.start_post += posts
        return num

    def metadata(self):
        if not self.next:
            max_page = 50 if self.logged_in else 25
            if self.start_page > max_page:
                self.log.info("Traversing from page %d to page %d",
                              max_page, self.start_page)
                self.start_post += self.per_page * (self.start_page - max_page)
                self.start_page = max_page

        tags = self.tags.split()
        if not self.logged_in and len(tags) > 4:
            raise exception.StopExtraction(
                "Non-members can only search up to 4 tags at once")
        return {"search_tags": " ".join(tags)}

    def post_ids(self):
        params = {"tags": self.tags}

        if self.next:
            params["next"] = self.next
        else:
            params["page"] = self.start_page

        while True:
            page = self.request(self.root, params=params, retries=10).text
            pos = page.find("<div id=more-popular-posts-link>") + 1
            yield from text.extract_iter(page, '" id=p', '>', pos)

            next_url = text.extract(page, 'next-page-url="', '"', pos)[0]
            if not next_url:
                return

            next_params = text.parse_query(text.unescape(
                next_url).lstrip("?/"))

            if "next" in next_params:
                # stop if the same "next" value occurs twice in a row (#265)
                if "next" in params and params["next"] == next_params["next"]:
                    return
                next_params["page"] = "2"
            params = next_params


class IdolcomplexPoolExtractor(IdolcomplexExtractor):
    """Extractor for image-pools from idol.sankakucomplex.com"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = r"(?:https?://)?idol\.sankakucomplex\.com/pool/show/(\d+)"
    test = ("https://idol.sankakucomplex.com/pool/show/145", {
        "count": 3,
    })
    per_page = 24

    def __init__(self, match):
        IdolcomplexExtractor.__init__(self, match)
        self.pool_id = match.group(1)

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        return num

    def metadata(self):
        return {"pool": self.pool_id}

    def post_ids(self):
        url = self.root + "/pool/show/" + self.pool_id
        params = {"page": self.start_page}

        while True:
            page = self.request(url, params=params, retries=10).text
            ids = list(text.extract_iter(page, '" id=p', '>'))

            yield from ids
            if len(ids) < self.per_page:
                return
            params["page"] += 1


class IdolcomplexPostExtractor(IdolcomplexExtractor):
    """Extractor for single images from idol.sankakucomplex.com"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?idol\.sankakucomplex\.com/post/show/(\d+)"
    test = ("https://idol.sankakucomplex.com/post/show/694215", {
        "content": "694ec2491240787d75bf5d0c75d0082b53a85afd",
        "options": (("tags", True),),
        "keyword": {
            "tags_character": "shani_(the_witcher)",
            "tags_copyright": "the_witcher",
            "tags_idol": str,
            "tags_medium": str,
            "tags_general": str,
        },
    })

    def __init__(self, match):
        IdolcomplexExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def post_ids(self):
        return (self.post_id,)
