# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.furaffinity.net/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.|sfw\.)?f(?:u|x|xfu)raffinity\.net"


class FuraffinityExtractor(Extractor):
    """Base class for furaffinity extractors"""
    category = "furaffinity"
    directory_fmt = ("{category}", "{user!l}")
    filename_fmt = "{id}{title:? //}.{extension}"
    archive_fmt = "{id}"
    cookies_domain = ".furaffinity.net"
    cookies_names = ("a", "b")
    root = "https://www.furaffinity.net"
    _warning = True

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.offset = 0

    def _init(self):
        self.external = self.config("external", False)

        if self.config("descriptions") == "html":
            self._process_description = str.strip

        layout = self.config("layout")
        if layout and layout != "auto":
            self._new_layout = False if layout == "old" else True
        else:
            self._new_layout = None

        if self._warning:
            if not self.cookies_check(self.cookies_names):
                self.log.warning("no 'a' and 'b' session cookies set")
            FuraffinityExtractor._warning = False

    def items(self):
        metadata = self.metadata()
        for post_id in util.advance(self.posts(), self.offset):
            post = self._parse_post(post_id)
            if post:
                if metadata:
                    post.update(metadata)
                yield Message.Directory, post
                yield Message.Url, post["url"], post

                if self.external:
                    for url in text.extract_iter(
                            post["_description"], 'href="http', '"'):
                        yield Message.Queue, "http" + url, post

    def metadata(self):
        return None

    def skip(self, num):
        self.offset += num
        return num

    def _parse_post(self, post_id):
        url = "{}/view/{}/".format(self.root, post_id)
        extr = text.extract_from(self.request(url).text)

        if self._new_layout is None:
            self._new_layout = ("http-equiv=" not in extr("<meta ", ">"))

        path = extr('href="//d', '"')
        if not path:
            self.log.warning(
                "Unable to download post %s (\"%s\")",
                post_id, text.remove_html(
                    extr('System Message', '</section>') or
                    extr('System Message', '</table>')
                )
            )
            return None

        pi = text.parse_int
        rh = text.remove_html

        data = text.nameext_from_url(path, {
            "id" : pi(post_id),
            "url": "https://d" + path,
        })

        if self._new_layout:
            data["tags"] = text.split_html(extr(
                'class="tags-row">', '</section>'))
            data["title"] = text.unescape(extr("<h2><p>", "</p></h2>"))
            data["artist"] = extr("<strong>", "<")
            data["_description"] = extr(
                'class="submission-description user-submitted-links">',
                '                                    </div>')
            data["views"] = pi(rh(extr('class="views">', '</span>')))
            data["favorites"] = pi(rh(extr('class="favorites">', '</span>')))
            data["comments"] = pi(rh(extr('class="comments">', '</span>')))
            data["rating"] = rh(extr('class="rating">', '</span>'))
            data["fa_category"] = rh(extr('>Category</strong>', '</span>'))
            data["theme"] = rh(extr('>', '<'))
            data["species"] = rh(extr('>Species</strong>', '</div>'))
            data["gender"] = rh(extr('>Gender</strong>', '</div>'))
            data["width"] = pi(extr("<span>", "x"))
            data["height"] = pi(extr("", "p"))
        else:
            # old site layout
            data["title"] = text.unescape(extr("<h2>", "</h2>"))
            data["artist"] = extr(">", "<")
            data["fa_category"] = extr("<b>Category:</b>", "<").strip()
            data["theme"] = extr("<b>Theme:</b>", "<").strip()
            data["species"] = extr("<b>Species:</b>", "<").strip()
            data["gender"] = extr("<b>Gender:</b>", "<").strip()
            data["favorites"] = pi(extr("<b>Favorites:</b>", "<"))
            data["comments"] = pi(extr("<b>Comments:</b>", "<"))
            data["views"] = pi(extr("<b>Views:</b>", "<"))
            data["width"] = pi(extr("<b>Resolution:</b>", "x"))
            data["height"] = pi(extr("", "<"))
            data["tags"] = text.split_html(extr(
                'id="keywords">', '</div>'))[::2]
            data["rating"] = extr('<img alt="', ' ')
            data["_description"] = extr(
                '<td valign="top" align="left" width="70%" class="alt1" '
                'style="padding:8px">', '                               </td>')

        data["artist_url"] = data["artist"].replace("_", "").lower()
        data["user"] = self.user or data["artist_url"]
        data["date"] = text.parse_timestamp(data["filename"].partition(".")[0])
        data["description"] = self._process_description(data["_description"])

        return data

    @staticmethod
    def _process_description(description):
        return text.unescape(text.remove_html(description, "", ""))

    def _pagination(self, path):
        num = 1

        while True:
            url = "{}/{}/{}/{}/".format(
                self.root, path, self.user, num)
            page = self.request(url).text
            post_id = None

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not post_id:
                return
            num += 1

    def _pagination_favorites(self):
        path = "/favorites/{}/".format(self.user)

        while path:
            page = self.request(self.root + path).text
            extr = text.extract_from(page)
            while True:
                post_id = extr('id="sid-', '"')
                if not post_id:
                    break
                self._favorite_id = text.parse_int(extr('data-fav-id="', '"'))
                yield post_id
            path = text.extr(page, 'right" href="', '"')

    def _pagination_search(self, query):
        url = self.root + "/search/"
        data = {
            "page"           : 1,
            "order-by"       : "relevancy",
            "order-direction": "desc",
            "range"          : "all",
            "range_from"     : "",
            "range_to"       : "",
            "rating-general" : "1",
            "rating-mature"  : "1",
            "rating-adult"   : "1",
            "type-art"       : "1",
            "type-music"     : "1",
            "type-flash"     : "1",
            "type-story"     : "1",
            "type-photo"     : "1",
            "type-poetry"    : "1",
            "mode"           : "extended",
        }

        data.update(query)
        if "page" in query:
            data["page"] = text.parse_int(query["page"])

        while True:
            page = self.request(url, method="POST", data=data).text
            post_id = None

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not post_id:
                return

            if "next_page" in data:
                data["page"] += 1
            else:
                data["next_page"] = "Next"


class FuraffinityGalleryExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's gallery"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)"
    example = "https://www.furaffinity.net/gallery/USER/"

    def posts(self):
        return self._pagination("gallery")


class FuraffinityScrapsExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user!l}", "Scraps")
    pattern = BASE_PATTERN + r"/scraps/([^/?#]+)"
    example = "https://www.furaffinity.net/scraps/USER/"

    def posts(self):
        return self._pagination("scraps")


class FuraffinityFavoriteExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user!l}", "Favorites")
    pattern = BASE_PATTERN + r"/favorites/([^/?#]+)"
    example = "https://www.furaffinity.net/favorites/USER/"

    def posts(self):
        return self._pagination_favorites()

    def _parse_post(self, post_id):
        post = FuraffinityExtractor._parse_post(self, post_id)
        if post:
            post["favorite_id"] = self._favorite_id
        return post


class FuraffinitySearchExtractor(FuraffinityExtractor):
    """Extractor for furaffinity search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = BASE_PATTERN + r"/search(?:/([^/?#]+))?/?[?&]([^#]+)"
    example = "https://www.furaffinity.net/search/?q=QUERY"

    def __init__(self, match):
        FuraffinityExtractor.__init__(self, match)
        self.query = text.parse_query(match.group(2))
        if self.user and "q" not in self.query:
            self.query["q"] = text.unquote(self.user)

    def metadata(self):
        return {"search": self.query.get("q")}

    def posts(self):
        return self._pagination_search(self.query)


class FuraffinityPostExtractor(FuraffinityExtractor):
    """Extractor for individual posts on furaffinity"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:view|full)/(\d+)"
    example = "https://www.furaffinity.net/view/12345/"

    def posts(self):
        post_id = self.user
        self.user = None
        return (post_id,)


class FuraffinityUserExtractor(FuraffinityExtractor):
    """Extractor for furaffinity user profiles"""
    subcategory = "user"
    cookies_domain = None
    pattern = BASE_PATTERN + r"/user/([^/?#]+)"
    example = "https://www.furaffinity.net/user/USER/"

    def initialize(self):
        pass

    skip = Extractor.skip

    def items(self):
        base = "{}/{{}}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (FuraffinityGalleryExtractor , base.format("gallery")),
            (FuraffinityScrapsExtractor  , base.format("scraps")),
            (FuraffinityFavoriteExtractor, base.format("favorites")),
        ), ("gallery",))


class FuraffinityFollowingExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's watched users"""
    subcategory = "following"
    pattern = BASE_PATTERN + "/watchlist/by/([^/?#]+)"
    example = "https://www.furaffinity.net/watchlist/by/USER/"

    def items(self):
        url = "{}/watchlist/by/{}/".format(self.root, self.user)
        data = {"_extractor": FuraffinityUserExtractor}

        while True:
            page = self.request(url).text

            for path in text.extract_iter(page, '<a href="', '"'):
                yield Message.Queue, self.root + path, data

            path = text.rextract(page, 'action="', '"')[0]
            if url.endswith(path):
                return
            url = self.root + path
