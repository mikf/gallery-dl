# -*- coding: utf-8 -*-

# Copyright 2020-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.furaffinity.net/"""

from .common import Extractor, Message, Dispatch
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.|sfw\.)?(?:f[ux]|f?xfu)raffinity\.net"


class FuraffinityExtractor(Extractor):
    """Base class for furaffinity extractors"""
    category = "furaffinity"
    directory_fmt = ("{category}", "{user!l}")
    filename_fmt = "{id}{title:? //}.{extension}"
    archive_fmt = "{id}"
    cookies_domain = ".furaffinity.net"
    cookies_names = ("a", "b")
    root = "https://www.furaffinity.net"
    request_interval = 1.0
    _warning = True

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match[1]
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
            if post := self._parse_post(post_id):
                if metadata:
                    post.update(metadata)
                yield Message.Directory, "", post
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
        url = f"{self.root}/view/{post_id}/"
        extr = text.extract_from(self.request(url).text)

        if self._new_layout is None:
            self._new_layout = ("http-equiv=" not in extr("<meta ", ">"))

        path = extr('href="//d', '"')
        if not path:
            msg = text.remove_html(
                extr('System Message', '</section>') or
                extr('System Message', '</table>')
            ).partition(" . Continue ")[0]
            return self.log.warning(
                "Unable to download post %s (\"%s\")", post_id, msg)

        pi = text.parse_int
        rh = text.remove_html

        data = text.nameext_from_url(path, {
            "id" : pi(post_id),
            "url": "https://d" + path,
        })

        if self._new_layout:
            data["tags"] = text.split_html(extr(
                "<h3>Keywords</h3>", "</section>"))
            data["scraps"] = (extr(' submissions">', "<") == "Scraps")
            data["title"] = text.unescape(extr("<h2><p>", "</p></h2>"))
            data["artist_url"] = extr('title="', '"').strip()
            data["artist"] = extr(">", "<")
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
            data["folders"] = folders = []
            for folder in extr(
                    "<h3>Listed in Folders</h3>", "</section>").split("</a>"):
                if folder := rh(folder):
                    folders.append(folder)
        else:
            # old site layout
            data["scraps"] = (
                "/scraps/" in extr('class="minigallery-title', "</a>"))
            data["title"] = text.unescape(extr("<h2>", "</h2>"))
            data["artist_url"] = extr('title="', '"').strip()
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
            data["folders"] = ()  # folders not present in old layout

        data["user"] = self.user or data["artist_url"]
        data["date"] = self.parse_timestamp(data["filename"].partition(".")[0])
        data["description"] = self._process_description(data["_description"])
        data["thumbnail"] = (f"https://t.furaffinity.net/{post_id}@600-"
                             f"{path.rsplit('/', 2)[1]}.jpg")
        return data

    def _process_description(self, description):
        return text.unescape(text.remove_html(description, "", ""))

    def _pagination(self, path, folder=None):
        num = 1
        folder = "" if folder is None else f"/folder/{folder}/a"

        while True:
            url = f"{self.root}/{path}/{self.user}{folder}/{num}/"
            page = self.request(url).text
            post_id = None

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not post_id:
                return
            num += 1

    def _pagination_favorites(self):
        path = f"/favorites/{self.user}/"

        while path:
            page = self.request(self.root + path).text
            extr = text.extract_from(page)
            while True:
                post_id = extr('id="sid-', '"')
                if not post_id:
                    break
                self._favorite_id = text.parse_int(extr('data-fav-id="', '"'))
                yield post_id

            pos = page.find('type="submit">Next</button>')
            if pos >= 0:
                path = text.rextr(page, '<form action="', '"', pos)
                continue
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
    pattern = rf"{BASE_PATTERN}/gallery/([^/?#]+)(?:$|/(?!folder/))"
    example = "https://www.furaffinity.net/gallery/USER/"

    def posts(self):
        return self._pagination("gallery")


class FuraffinityFolderExtractor(FuraffinityExtractor):
    """Extractor for a FurAffinity folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{user!l}",
                     "Folders", "{folder_id}{folder_name:? //}")
    pattern = rf"{BASE_PATTERN}/gallery/([^/?#]+)/folder/(\d+)(?:/([^/?#]+))?"
    example = "https://www.furaffinity.net/gallery/USER/folder/12345/FOLDER"

    def metadata(self):
        return {
            "folder_id"  : self.groups[1],
            "folder_name": self.groups[2] or "",
        }

    def posts(self):
        return self._pagination("gallery", self.groups[1])


class FuraffinityScrapsExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user!l}", "Scraps")
    pattern = rf"{BASE_PATTERN}/scraps/([^/?#]+)"
    example = "https://www.furaffinity.net/scraps/USER/"

    def posts(self):
        return self._pagination("scraps")


class FuraffinityFavoriteExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user!l}", "Favorites")
    pattern = rf"{BASE_PATTERN}/favorites/([^/?#]+)"
    example = "https://www.furaffinity.net/favorites/USER/"

    def posts(self):
        return self._pagination_favorites()

    def _parse_post(self, post_id):
        if post := FuraffinityExtractor._parse_post(self, post_id):
            post["favorite_id"] = self._favorite_id
        return post


class FuraffinitySearchExtractor(FuraffinityExtractor):
    """Extractor for furaffinity search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = rf"{BASE_PATTERN}/search(?:/([^/?#]+))?/?[?&]([^#]+)"
    example = "https://www.furaffinity.net/search/?q=QUERY"

    def __init__(self, match):
        FuraffinityExtractor.__init__(self, match)
        self.query = text.parse_query(match[2])
        if self.user and "q" not in self.query:
            self.query["q"] = text.unquote(self.user)

    def metadata(self):
        return {"search": self.query.get("q")}

    def posts(self):
        return self._pagination_search(self.query)


class FuraffinityPostExtractor(FuraffinityExtractor):
    """Extractor for individual posts on furaffinity"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?:view|full)/(\d+)"
    example = "https://www.furaffinity.net/view/12345/"

    def posts(self):
        post_id = self.user
        self.user = None
        return (post_id,)


class FuraffinityUserExtractor(Dispatch, FuraffinityExtractor):
    """Extractor for furaffinity user profiles"""
    pattern = rf"{BASE_PATTERN}/user/([^/?#]+)"
    example = "https://www.furaffinity.net/user/USER/"

    def items(self):
        base = self.root
        user = f"{self.user}/"
        return self._dispatch_extractors((
            (FuraffinityGalleryExtractor , f"{base}/gallery/{user}"),
            (FuraffinityScrapsExtractor  , f"{base}/scraps/{user}"),
            (FuraffinityFavoriteExtractor, f"{base}/favorites/{user}"),
        ), ("gallery",))


class FuraffinityFollowingExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's watched users"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/watchlist/by/([^/?#]+)"
    example = "https://www.furaffinity.net/watchlist/by/USER/"

    def items(self):
        url = f"{self.root}/watchlist/by/{self.user}/"
        data = {"_extractor": FuraffinityUserExtractor}

        while True:
            page = self.request(url).text

            for path in text.extract_iter(page, '<a href="', '"'):
                yield Message.Queue, self.root + path, data

            path = text.rextr(page, 'action="', '"')
            if url.endswith(path):
                return
            url = self.root + path


class FuraffinitySubmissionsExtractor(FuraffinityExtractor):
    """Extractor for new furaffinity submissions"""
    subcategory = "submissions"
    pattern = rf"{BASE_PATTERN}(/msg/submissions(?:/[^/?#]+)?)"
    example = "https://www.furaffinity.net/msg/submissions"

    def posts(self):
        self.user = None
        url = self.root + self.groups[0]
        return self._pagination_submissions(url)

    def _pagination_submissions(self, url):
        while True:
            page = self.request(url).text

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if (pos := page.find(">Next 48</a>")) < 0 and \
                    (pos := page.find(">&gt;&gt;&gt; Next 48 &gt;&gt;")) < 0:
                return

            path = text.rextr(page, 'href="', '"', pos)
            url = self.root + text.unescape(path)
