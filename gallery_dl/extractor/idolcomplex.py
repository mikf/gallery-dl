# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
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

BASE_PATTERN = r"(?:https?://)?idol\.sankakucomplex\.com(?:/[a-z]{2})?"


class IdolcomplexExtractor(SankakuExtractor):
    """Base class for idolcomplex extractors"""
    category = "idolcomplex"
    root = "https://idol.sankakucomplex.com"
    cookies_domain = "idol.sankakucomplex.com"
    cookies_names = ("_idolcomplex_session",)
    referer = False
    request_interval = (3.0, 6.0)

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.logged_in = True
        self.start_page = 1
        self.start_post = 0

    def _init(self):
        self.find_pids = re.compile(
            r" href=[\"#]/\w\w/posts/(\w+)"
        ).findall
        self.find_tags = re.compile(
            r'tag-type-([^"]+)">\s*<a [^>]*?href="/[^?]*\?tags=([^"]+)'
        ).findall

    def items(self):
        self.login()
        data = self.metadata()

        for post_id in util.advance(self.post_ids(), self.start_post):
            post = self._extract_post(post_id)
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
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

        self.logged_in = False

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/users/login"
        page = self.request(url).text

        headers = {
            "Referer": url,
        }
        url = self.root + (text.extr(page, '<form action="', '"') or
                           "/en/user/authenticate")
        data = {
            "authenticity_token": text.unescape(text.extr(
                page, 'name="authenticity_token" value="', '"')),
            "url"           : "",
            "user[name]"    : username,
            "user[password]": password,
            "commit"        : "Login",
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.history or response.url.endswith("/user/home"):
            raise exception.AuthenticationError()
        return {c.name: c.value for c in response.history[0].cookies}

    def _extract_post(self, post_id):
        url = self.root + "/posts/" + post_id
        page = self.request(url, retries=10).text
        extr = text.extract_from(page)

        vavg = extr('id="rating"', "</ul>")
        vcnt = extr('>Votes</strong>:', "<")
        pid = extr(">Post ID:", "<")
        created = extr(' title="', '"')

        file_url = extr('>Original:', 'id=')
        if file_url:
            file_url = extr(' href="', '"')
            width = extr(">", "x")
            height = extr("", " ")
        else:
            width = extr('<object width=', ' ')
            height = extr('height=', '>')
            file_url = extr('<embed src="', '"')

        rating = extr(">Rating:", "<br")

        data = {
            "id"          : pid.strip(),
            "md5"         : file_url.rpartition("/")[2].partition(".")[0],
            "vote_average": (1.0 * vavg.count('class="star-full"') +
                             0.5 * vavg.count('class="star-half"')),
            "vote_count"  : text.parse_int(vcnt),
            "created_at"  : created,
            "date"        : text.parse_datetime(
                created, "%Y-%m-%d %H:%M:%S.%f"),
            "rating"      : text.remove_html(rating).lower(),
            "file_url"    : "https:" + text.unescape(file_url),
            "width"       : text.parse_int(width),
            "height"      : text.parse_int(height),
        }

        tags = collections.defaultdict(list)
        tags_list = []
        tags_html = text.extr(page, '<ul id="tag-sidebar"', '</ul>')
        for tag_type, tag_name in self.find_tags(tags_html or ""):
            tags[tag_type].append(text.unquote(tag_name))
        for key, value in tags.items():
            data["tags_" + key] = " ".join(value)
            tags_list += value
        data["tags"] = " ".join(tags_list)

        return data


class IdolcomplexTagExtractor(IdolcomplexExtractor):
    """Extractor for images from idol.sankakucomplex.com by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/(?:posts/?)?\?([^#]*)"
    example = "https://idol.sankakucomplex.com/en/posts?tags=TAGS"
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
            pos = ((page.find('id="more-popular-posts-link"') + 1) or
                   (page.find('<span class="thumb') + 1))

            yield from self.find_pids(page, pos)

            next_url = text.extract(page, 'next-page-url="', '"', pos)[0]
            if not next_url:
                return

            next_params = text.parse_query(text.unquote(text.unescape(
                text.unescape(next_url).lstrip("?/"))))

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
    pattern = BASE_PATTERN + r"/pools?/(?:show/)?(\w+)"
    example = "https://idol.sankakucomplex.com/pools/0123456789abcdef"
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
        url = self.root + "/pools/show/" + self.pool_id
        params = {"page": self.start_page}

        while True:
            page = self.request(url, params=params, retries=10).text
            pos = page.find('id="pool-show"') + 1
            post_ids = self.find_pids(page, pos)

            yield from post_ids
            if len(post_ids) < self.per_page:
                return
            params["page"] += 1


class IdolcomplexPostExtractor(IdolcomplexExtractor):
    """Extractor for single images from idol.sankakucomplex.com"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/posts?/(?:show/)?(\w+)"
    example = "https://idol.sankakucomplex.com/posts/0123456789abcdef"

    def __init__(self, match):
        IdolcomplexExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def post_ids(self):
        return (self.post_id,)
