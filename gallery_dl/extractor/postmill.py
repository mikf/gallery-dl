# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Postmill instances"""

import re
from .common import BaseExtractor, Message
from .. import text, exception


class PostmillExtractor(BaseExtractor):
    """Base class for Postmill extractors"""
    basecategory = "postmill"
    directory_fmt = ("{category}", "{instance}", "{forum}")
    filename_fmt = "{id}_{title[:220]}.{extension}"
    archive_fmt = "{filename}"

    def _init(self):
        self.instance = self.root.partition("://")[2]
        self.save_link_post_body = self.config("save-link-post-body", False)
        self._search_canonical_url = re.compile(r"/f/([\w\d_]+)/(\d+)/").search
        self._search_image_tag = re.compile(
            r'<a href="[^"]+"\n +class="submission__image-link"').search

    def items(self):
        for post_url in self.post_urls():
            page = self.request(post_url).text
            extr = text.extract_from(page)

            title = text.unescape(extr(
                '<meta property="og:title" content="', '">'))
            date = text.parse_datetime(extr(
                '<meta property="og:article:published_time" content="', '">'))
            username = extr(
                '<meta property="og:article:author" content="', '">')
            post_canonical_url = text.unescape(extr(
                '<link rel="canonical" href="', '">'))

            url = text.unescape(extr(
                '<h1 class="submission__title unheaderize inline"><a href="',
                '"'))
            body = extr(
                '<div class="submission__body break-text text-flow">',
                '</div>')

            match = self._search_canonical_url(post_canonical_url)
            forum = match.group(1)
            id = int(match.group(2))

            is_text_post = (url[0] == "/")
            is_image_post = self._search_image_tag(page) is not None
            data = {
                "title": title,
                "date": date,
                "username": username,
                "forum": forum,
                "id": id,
                "flair": [text.unescape(i) for i in text.extract_iter(
                    page, '<span class="flair__label">', '</span>')],
                "instance": self.instance,
            }

            urls = []
            if is_text_post or self.save_link_post_body:
                urls.append((Message.Url, "text:" + body))

            if is_image_post:
                urls.append((Message.Url, url))
            elif not is_text_post:
                urls.append((Message.Queue, url))

            data["count"] = len(urls)
            yield Message.Directory, data
            for data["num"], (msg, url) in enumerate(urls, 1):
                if url.startswith("text:"):
                    data["filename"], data["extension"] = "", "htm"
                else:
                    data = text.nameext_from_url(url, data)

                yield msg, url, data


class PostmillSubmissionsExtractor(PostmillExtractor):
    """Base class for Postmill submissions extractors"""
    whitelisted_parameters = ()

    def __init__(self, match):
        PostmillExtractor.__init__(self, match)
        groups = match.groups()
        self.base = groups[-3]
        self.sorting_path = groups[-2] or ""
        self.query = {key: value for key, value in text.parse_query(
            groups[-1]).items() if self.acceptable_query(key)}

    def items(self):
        url = self.root + self.base + self.sorting_path

        while url:
            response = self.request(url, params=self.query)
            if response.history:
                redirect_url = response.url
                if redirect_url == self.root + "/login":
                    raise exception.StopExtraction(
                        "HTTP redirect to login page (%s)", redirect_url)
            page = response.text

            for nav in text.extract_iter(page,
                                         '<nav class="submission__nav">',
                                         '</nav>'):
                post_url = text.unescape(text.extr(nav, '<a href="', '"'))
                yield Message.Queue, text.urljoin(url, post_url), \
                    {"_extractor": PostmillPostExtractor}

            url = text.unescape(text.extr(page,
                                          '<link rel="next" href="', '">'))

    def acceptable_query(self, key):
        return key in self.whitelisted_parameters or key == "t" or \
            (key.startswith("next[") and key.endswith("]"))


BASE_PATTERN = PostmillExtractor.update({
    "raddle": {
        "root"   : None,
        "pattern": (r"(?:raddle\.me|"
                    r"c32zjeghcp5tj3kb72pltz56piei66drc63vkhn5yixiyk4cmerrjtid"
                    r"\.onion)"),
    }
})
QUERY_RE = r"(?:\?([^#]+))?$"
SORTING_RE = r"(/(?:hot|new|active|top|controversial|most_commented))?" + \
    QUERY_RE


class PostmillPostExtractor(PostmillExtractor):
    """Extractor for a single submission URL"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/f/(\w+)/(\d+)"
    example = "https://raddle.me/f/FORUM/123/TITLE"

    def __init__(self, match):
        PostmillExtractor.__init__(self, match)
        self.forum = match.group(3)
        self.post_id = match.group(4)

    def post_urls(self):
        return (self.root + "/f/" + self.forum + "/" + self.post_id,)


class PostmillShortURLExtractor(PostmillExtractor):
    """Extractor for short submission URLs"""
    subcategory = "shorturl"
    pattern = BASE_PATTERN + r"/(\d+)$"
    example = "https://raddle.me/123"

    def __init__(self, match):
        PostmillExtractor.__init__(self, match)
        self.post_id = match.group(3)

    def items(self):
        url = self.root + "/" + self.post_id
        response = self.request(url, method="HEAD", allow_redirects=False)
        full_url = text.urljoin(url, response.headers["Location"])
        yield Message.Queue, full_url, {"_extractor": PostmillPostExtractor}


class PostmillHomeExtractor(PostmillSubmissionsExtractor):
    """Extractor for the home page"""
    subcategory = "home"
    pattern = BASE_PATTERN + r"(/(?:featured|subscribed|all)?)" + SORTING_RE
    example = "https://raddle.me/"


class PostmillForumExtractor(PostmillSubmissionsExtractor):
    """Extractor for submissions on a forum"""
    subcategory = "forum"
    pattern = BASE_PATTERN + r"(/f/\w+)" + SORTING_RE
    example = "https://raddle.me/f/FORUM"


class PostmillUserSubmissionsExtractor(PostmillSubmissionsExtractor):
    """Extractor for submissions made by a user"""
    subcategory = "usersubmissions"
    pattern = BASE_PATTERN + r"(/user/\w+/submissions)()" + QUERY_RE
    example = "https://raddle.me/user/USER/submissions"


class PostmillTagExtractor(PostmillSubmissionsExtractor):
    """Extractor for submissions on a forum with a specific tag"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"(/tag/\w+)" + SORTING_RE
    example = "https://raddle.me/tag/TAG"


class PostmillSearchExtractor(PostmillSubmissionsExtractor):
    """Extractor for search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"(/search)()\?(q=[^#]+)$"
    example = "https://raddle.me/search?q=QUERY"
    whitelisted_parameters = ("q",)
