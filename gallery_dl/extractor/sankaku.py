# -*- coding: utf-8 -*-

# Copyright 2014-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://chan.sankakucomplex.com/"""

from .common import Extractor, Message, SharedConfigMixin
from .. import text, util, exception
from ..cache import cache
import collections
import random
import time
import re


class SankakuExtractor(SharedConfigMixin, Extractor):
    """Base class for sankaku extractors"""
    basecategory = "booru"
    category = "sankaku"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    cookienames = ("login", "pass_hash")
    cookiedomain = "chan.sankakucomplex.com"
    subdomain = "chan"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = "https://" + self.cookiedomain
        self.logged_in = True
        self.start_page = 1
        self.start_post = 0
        self.extags = self.config("tags", False)
        self.wait_min = self.config("wait-min", 3.0)
        self.wait_max = self.config("wait-max", 6.0)
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min

    def items(self):
        self.login()

        yield Message.Version, 1
        data = self.get_metadata()

        for post_id in util.advance(self.get_posts(), self.start_post):
            self.wait()
            post = self.get_post_data(post_id)
            url = post["file_url"]
            post.update(data)
            text.nameext_from_url(url, post)
            yield Message.Directory, post
            yield Message.Url, url, post

    def skip(self, num):
        self.start_post += num
        return num

    def get_metadata(self):
        """Return general metadata"""
        return {}

    def get_posts(self):
        """Return an iterable containing all relevant post ids"""

    def get_post_data(self, post_id, extr=text.extract):
        """Extract metadata of a single post"""
        url = self.root + "/post/show/" + post_id
        page = self.request(url, retries=10).text

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

    def wait(self):
        """Wait for a randomly chosen amount of seconds"""
        time.sleep(random.uniform(self.wait_min, self.wait_max))

    def login(self):
        """Login and set necessary cookies"""
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            cookies = self._login_impl((username, self.subdomain), password)
            self._update_cookies(cookies)
        else:
            self.logged_in = False

    @cache(maxage=90*24*3600, keyarg=1)
    def _login_impl(self, usertuple, password):
        username = usertuple[0]
        self.log.info("Logging in as %s", username)
        url = self.root + "/user/authenticate"
        data = {
            "url": "",
            "user[name]": username,
            "user[password]": password,
            "commit": "Login",
        }
        response = self.request(url, method="POST", data=data)

        if not response.history or response.url != self.root + "/user/home":
            raise exception.AuthenticationError()
        cookies = response.history[0].cookies
        return {c: cookies[c] for c in self.cookienames}


class SankakuTagExtractor(SankakuExtractor):
    """Extractor for images from chan.sankakucomplex.com by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = r"(?:https?://)?chan\.sankakucomplex\.com/\?([^#]*)"
    test = (
        ("https://chan.sankakucomplex.com/?tags=bonocho", {
            "count": 5,
            "pattern": r"https://c?s\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}"
                       r"/[^/]{32}\.\w+\?e=\d+&m=[^&#]+",
        }),
        # respect 'page' query parameter
        ("https://chan.sankakucomplex.com/?tags=bonocho&page=2", {
            "count": 0,
        }),
        # respect 'next' query parameter
        ("https://chan.sankakucomplex.com/?tags=bonocho&next=182284", {
            "count": 1,
        }),
        # error on five or more tags
        ("https://chan.sankakucomplex.com/?tags=bonocho+a+b+c+d", {
            "options": (("username", None),),
            "exception": exception.StopExtraction,
        }),
        # match arbitrary query parameters
        ("https://chan.sankakucomplex.com"
         "/?tags=marie_rose&page=98&next=3874906&commit=Search"),
    )
    per_page = 20

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
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

    def get_metadata(self):
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
                "Unauthenticated users cannot use more than 4 tags at once.")
        return {"search_tags": " ".join(tags)}

    def get_posts(self):
        params = {"tags": self.tags}

        if self.next:
            params["next"] = self.next
        else:
            params["page"] = self.start_page

        while True:
            self.wait()
            page = self.request(self.root, params=params, retries=10).text
            pos = page.find("<div id=more-popular-posts-link>") + 1

            ids = list(text.extract_iter(page, '" id=p', '>', pos))
            if not ids:
                return
            yield from ids

            next_qs = text.extract(page, 'next-page-url="/?', '"', pos)[0]
            next_id = text.parse_query(next_qs).get("next")

            # stop if the same "next" parameter occurs twice in a row (#265)
            if "next" in params and params["next"] == next_id:
                return

            params["next"] = next_id or (text.parse_int(ids[-1]) - 1)
            params["page"] = "2"


class SankakuPoolExtractor(SankakuExtractor):
    """Extractor for image-pools  from chan.sankakucomplex.com"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = r"(?:https?://)?chan\.sankakucomplex\.com/pool/show/(\d+)"
    test = ("https://chan.sankakucomplex.com/pool/show/90", {
        "count": 5,
    })
    per_page = 24

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.pool_id = match.group(1)

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        return num

    def get_metadata(self):
        return {"pool": self.pool_id}

    def get_posts(self):
        url = self.root + "/pool/show/" + self.pool_id
        params = {"page": self.start_page}

        while True:
            page = self.request(url, params=params, retries=10).text
            ids = list(text.extract_iter(page, '" id=p', '>'))

            yield from ids
            if len(ids) < self.per_page:
                return

            params["page"] += 1


class SankakuPostExtractor(SankakuExtractor):
    """Extractor for single images from chan.sankakucomplex.com"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?chan\.sankakucomplex\.com/post/show/(\d+)"
    test = ("https://chan.sankakucomplex.com/post/show/360451", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
        "options": (("tags", True),),
        "keyword": {
            "tags_artist": "bonocho",
            "tags_studio": "dc_comics",
            "tags_medium": "sketch copyright_name",
            "tags_copyright": str,
            "tags_character": str,
            "tags_general": str,
        },
    })

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def get_posts(self):
        return (self.post_id,)
