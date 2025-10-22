# -*- coding: utf-8 -*-

# Copyright 2020-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://inkbunny.net/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?inkbunny\.net"


class InkbunnyExtractor(Extractor):
    """Base class for inkbunny extractors"""
    category = "inkbunny"
    directory_fmt = ("{category}", "{username!l}")
    filename_fmt = "{submission_id} {file_id} {title}.{extension}"
    archive_fmt = "{file_id}"
    root = "https://inkbunny.net"

    def _init(self):
        self.api = self.utils().InkbunnyAPI(self)

    def items(self):
        self.api.authenticate()
        metadata = self.metadata()
        to_bool = ("deleted", "favorite", "friends_only", "guest_block",
                   "hidden", "public", "scraps")

        for post in self.posts():
            post.update(metadata)
            post["date"] = self.parse_datetime_iso(
                post["create_datetime"][:19])
            post["tags"] = [kw["keyword_name"] for kw in post["keywords"]]
            post["ratings"] = [r["name"] for r in post["ratings"]]
            files = post["files"]

            for key in to_bool:
                if key in post:
                    post[key] = (post[key] == "t")

            del post["keywords"]
            del post["files"]

            yield Message.Directory, post
            for post["num"], file in enumerate(files, 1):
                post.update(file)
                post["deleted"] = (file["deleted"] == "t")
                post["date"] = self.parse_datetime_iso(
                    file["create_datetime"][:19])
                text.nameext_from_url(file["file_name"], post)

                url = file["file_url_full"]
                if "/private_files/" in url:
                    url = f"{url}?sid={self.api.session_id}"
                yield Message.Url, url, post

    def posts(self):
        return ()

    def metadata(self):
        return ()


class InkbunnyUserExtractor(InkbunnyExtractor):
    """Extractor for inkbunny user profiles"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/(?!s/)(gallery/|scraps/)?(\w+)(?:$|[/?#])"
    example = "https://inkbunny.net/USER"

    def __init__(self, match):
        kind, self.user = match.groups()
        if not kind:
            self.scraps = None
        elif kind[0] == "g":
            self.subcategory = "gallery"
            self.scraps = "no"
        else:
            self.subcategory = "scraps"
            self.scraps = "only"
        InkbunnyExtractor.__init__(self, match)

    def posts(self):
        orderby = self.config("orderby")
        params = {
            "username": self.user,
            "scraps"  : self.scraps,
            "orderby" : orderby,
        }
        if orderby and orderby.startswith("unread_"):
            params["unread_submissions"] = "yes"
        return self.api.search(params)


class InkbunnyPoolExtractor(InkbunnyExtractor):
    """Extractor for inkbunny pools"""
    subcategory = "pool"
    pattern = (rf"{BASE_PATTERN}/(?:"
               rf"poolview_process\.php\?pool_id=(\d+)|"
               rf"submissionsviewall\.php"
               rf"\?((?:[^#]+&)?mode=pool(?:&[^#]+)?))")
    example = "https://inkbunny.net/poolview_process.php?pool_id=12345"

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        if pid := match[1]:
            self.pool_id = pid
            self.orderby = "pool_order"
        else:
            params = text.parse_query(match[2])
            self.pool_id = params.get("pool_id")
            self.orderby = params.get("orderby", "pool_order")

    def metadata(self):
        return {"pool_id": self.pool_id}

    def posts(self):
        params = {
            "pool_id": self.pool_id,
            "orderby": self.orderby,
        }
        return self.api.search(params)


class InkbunnyFavoriteExtractor(InkbunnyExtractor):
    """Extractor for inkbunny user favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{favs_username!l}", "Favorites")
    pattern = (rf"{BASE_PATTERN}/(?:"
               r"userfavorites_process\.php\?favs_user_id=(\d+)|"
               r"submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=userfavs(?:&[^#]+)?))")
    example = ("https://inkbunny.net/userfavorites_process.php"
               "?favs_user_id=12345")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        if uid := match[1]:
            self.user_id = uid
            self.orderby = self.config("orderby", "fav_datetime")
        else:
            params = text.parse_query(match[2])
            self.user_id = params.get("user_id")
            self.orderby = params.get("orderby", "fav_datetime")

    def metadata(self):
        # Lookup fav user ID as username
        url = (f"{self.root}/userfavorites_process.php"
               f"?favs_user_id={self.user_id}")
        page = self.request(url).text
        user_link = text.extr(page, '<a rel="author"', '</a>')
        favs_username = text.extr(user_link, 'href="/', '"')

        return {
            "favs_user_id": self.user_id,
            "favs_username": favs_username,
        }

    def posts(self):
        params = {
            "favs_user_id": self.user_id,
            "orderby"     : self.orderby,
        }
        if self.orderby and self.orderby.startswith("unread_"):
            params["unread_submissions"] = "yes"
        return self.api.search(params)


class InkbunnyUnreadExtractor(InkbunnyExtractor):
    """Extractor for unread inkbunny submissions"""
    subcategory = "unread"
    pattern = (rf"{BASE_PATTERN}/submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=unreadsubs(?:&[^#]+)?)")
    example = ("https://inkbunny.net/submissionsviewall.php"
               "?text=&mode=unreadsubs&type=")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        self.params = text.parse_query(match[1])

    def posts(self):
        params = self.params.copy()
        params.pop("rid", None)
        params.pop("mode", None)
        params["unread_submissions"] = "yes"
        return self.api.search(params)


class InkbunnySearchExtractor(InkbunnyExtractor):
    """Extractor for inkbunny search results"""
    subcategory = "search"
    pattern = (rf"{BASE_PATTERN}/submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=search(?:&[^#]+)?)")
    example = ("https://inkbunny.net/submissionsviewall.php"
               "?text=TAG&mode=search&type=")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        self.params = text.parse_query(match[1])

    def metadata(self):
        return {"search": self.params}

    def posts(self):
        params = self.params.copy()
        pop = params.pop

        pop("rid", None)
        params["string_join_type"] = pop("stringtype", None)
        params["dayslimit"] = pop("days", None)
        params["username"] = pop("artist", None)

        if favsby := pop("favsby", None):
            # get user_id from user profile
            url = f"{self.root}/{favsby}"
            page = self.request(url).text
            user_id = text.extr(page, "?user_id=", "'")
            params["favs_user_id"] = user_id.partition("&")[0]

        return self.api.search(params)


class InkbunnyFollowingExtractor(InkbunnyExtractor):
    """Extractor for inkbunny user watches"""
    subcategory = "following"
    pattern = (rf"{BASE_PATTERN}/(?:"
               r"watchlist_process\.php\?mode=watching&user_id=(\d+)|"
               r"usersviewall\.php"
               r"\?((?:[^#]+&)?mode=watching(?:&[^#]+)?))")
    example = ("https://inkbunny.net/watchlist_process.php"
               "?mode=watching&user_id=12345")

    def items(self):
        user_id, qs = self.groups
        if not user_id:
            user_id = text.parse_query(qs).get("user_id")
        url = f"{self.root}/watchlist_process.php"
        params = {"mode": "watching", "user_id": user_id}

        with self.request(url, params=params) as response:
            url, _, params = response.url.partition("?")
            page = response.text

        params = text.parse_query(params)
        params["page"] = text.parse_int(params.get("page"), 1)
        data = {"_extractor": InkbunnyUserExtractor}

        while True:
            for user in text.extract_iter(
                    page, '<a class="widget_userNameSmall" href="', '"',
                    page.index('id="changethumboriginal_form"')):
                yield Message.Queue, self.root + user, data

            if "<a title='next page' " not in page:
                return
            params["page"] += 1
            page = self.request(url, params=params).text


class InkbunnyPostExtractor(InkbunnyExtractor):
    """Extractor for individual Inkbunny posts"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/s/(\d+)"
    example = "https://inkbunny.net/s/12345"

    def posts(self):
        submissions = self.api.detail(({"submission_id": self.groups[0]},))
        if submissions[0] is None:
            raise exception.NotFoundError("submission")
        return submissions
