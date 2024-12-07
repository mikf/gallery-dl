# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://inkbunny.net/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache


BASE_PATTERN = r"(?:https?://)?(?:www\.)?inkbunny\.net"


class InkbunnyExtractor(Extractor):
    """Base class for inkbunny extractors"""
    category = "inkbunny"
    directory_fmt = ("{category}", "{username!l}")
    filename_fmt = "{submission_id} {file_id} {title}.{extension}"
    archive_fmt = "{file_id}"
    root = "https://inkbunny.net"

    def _init(self):
        self.api = InkbunnyAPI(self)

    def items(self):
        self.api.authenticate()
        metadata = self.metadata()
        to_bool = ("deleted", "favorite", "friends_only", "guest_block",
                   "hidden", "public", "scraps")

        for post in self.posts():
            post.update(metadata)
            post["date"] = text.parse_datetime(
                post["create_datetime"] + "00", "%Y-%m-%d %H:%M:%S.%f%z")
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
                post["date"] = text.parse_datetime(
                    file["create_datetime"] + "00", "%Y-%m-%d %H:%M:%S.%f%z")
                text.nameext_from_url(file["file_name"], post)

                url = file["file_url_full"]
                if "/private_files/" in url:
                    url += "?sid=" + self.api.session_id
                yield Message.Url, url, post

    def posts(self):
        return ()

    def metadata(self):
        return ()


class InkbunnyUserExtractor(InkbunnyExtractor):
    """Extractor for inkbunny user profiles"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!s/)(gallery/|scraps/)?(\w+)(?:$|[/?#])"
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
    pattern = (BASE_PATTERN + r"/(?:"
               r"poolview_process\.php\?pool_id=(\d+)|"
               r"submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=pool(?:&[^#]+)?))")
    example = "https://inkbunny.net/poolview_process.php?pool_id=12345"

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        pid = match.group(1)
        if pid:
            self.pool_id = pid
            self.orderby = "pool_order"
        else:
            params = text.parse_query(match.group(2))
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
    pattern = (BASE_PATTERN + r"/(?:"
               r"userfavorites_process\.php\?favs_user_id=(\d+)|"
               r"submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=userfavs(?:&[^#]+)?))")
    example = ("https://inkbunny.net/userfavorites_process.php"
               "?favs_user_id=12345")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        uid = match.group(1)
        if uid:
            self.user_id = uid
            self.orderby = self.config("orderby", "fav_datetime")
        else:
            params = text.parse_query(match.group(2))
            self.user_id = params.get("user_id")
            self.orderby = params.get("orderby", "fav_datetime")

    def metadata(self):
        # Lookup fav user ID as username
        url = "{}/userfavorites_process.php?favs_user_id={}".format(
            self.root, self.user_id)
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
    pattern = (BASE_PATTERN + r"/submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=unreadsubs(?:&[^#]+)?)")
    example = ("https://inkbunny.net/submissionsviewall.php"
               "?text=&mode=unreadsubs&type=")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def posts(self):
        params = self.params.copy()
        params.pop("rid", None)
        params.pop("mode", None)
        params["unread_submissions"] = "yes"
        return self.api.search(params)


class InkbunnySearchExtractor(InkbunnyExtractor):
    """Extractor for inkbunny search results"""
    subcategory = "search"
    pattern = (BASE_PATTERN + r"/submissionsviewall\.php"
               r"\?((?:[^#]+&)?mode=search(?:&[^#]+)?)")
    example = ("https://inkbunny.net/submissionsviewall.php"
               "?text=TAG&mode=search&type=")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def metadata(self):
        return {"search": self.params}

    def posts(self):
        params = self.params.copy()
        pop = params.pop

        pop("rid", None)
        params["string_join_type"] = pop("stringtype", None)
        params["dayslimit"] = pop("days", None)
        params["username"] = pop("artist", None)

        favsby = pop("favsby", None)
        if favsby:
            # get user_id from user profile
            url = "{}/{}".format(self.root, favsby)
            page = self.request(url).text
            user_id = text.extr(page, "?user_id=", "'")
            params["favs_user_id"] = user_id.partition("&")[0]

        return self.api.search(params)


class InkbunnyFollowingExtractor(InkbunnyExtractor):
    """Extractor for inkbunny user watches"""
    subcategory = "following"
    pattern = (BASE_PATTERN + r"/(?:"
               r"watchlist_process\.php\?mode=watching&user_id=(\d+)|"
               r"usersviewall\.php"
               r"\?((?:[^#]+&)?mode=watching(?:&[^#]+)?))")
    example = ("https://inkbunny.net/watchlist_process.php"
               "?mode=watching&user_id=12345")

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        self.user_id = match.group(1) or \
            text.parse_query(match.group(2)).get("user_id")

    def items(self):
        url = self.root + "/watchlist_process.php"
        params = {"mode": "watching", "user_id": self.user_id}

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
    pattern = BASE_PATTERN + r"/s/(\d+)"
    example = "https://inkbunny.net/s/12345"

    def __init__(self, match):
        InkbunnyExtractor.__init__(self, match)
        self.submission_id = match.group(1)

    def posts(self):
        submissions = self.api.detail(({"submission_id": self.submission_id},))
        if submissions[0] is None:
            raise exception.NotFoundError("submission")
        return submissions


class InkbunnyAPI():
    """Interface for the Inkunny API

    Ref: https://wiki.inkbunny.net/wiki/API
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.session_id = None

    def detail(self, submissions):
        """Get full details about submissions with the given IDs"""
        ids = {
            sub["submission_id"]: idx
            for idx, sub in enumerate(submissions)
        }
        params = {
            "submission_ids": ",".join(ids),
            "show_description": "yes",
        }

        submissions = [None] * len(ids)
        for sub in self._call("submissions", params)["submissions"]:
            submissions[ids[sub["submission_id"]]] = sub
        return submissions

    def search(self, params):
        """Perform a search"""
        return self._pagination_search(params)

    def set_allowed_ratings(self, nudity=True, sexual=True,
                            violence=True, strong_violence=True):
        """Change allowed submission ratings"""
        params = {
            "tag[2]": "yes" if nudity else "no",
            "tag[3]": "yes" if violence else "no",
            "tag[4]": "yes" if sexual else "no",
            "tag[5]": "yes" if strong_violence else "no",
        }
        self._call("userrating", params)

    def authenticate(self, invalidate=False):
        username, password = self.extractor._get_auth_info()
        if invalidate:
            _authenticate_impl.invalidate(username or "guest")
        if username:
            self.session_id = _authenticate_impl(self, username, password)
        else:
            self.session_id = _authenticate_impl(self, "guest", "")
            self.set_allowed_ratings()

    def _call(self, endpoint, params):
        url = "https://inkbunny.net/api_" + endpoint + ".php"

        while True:
            params["sid"] = self.session_id
            data = self.extractor.request(url, params=params).json()

            if "error_code" not in data:
                return data

            if str(data["error_code"]) == "2":
                self.authenticate(invalidate=True)
                continue

            raise exception.StopExtraction(data.get("error_message"))

    def _pagination_search(self, params):
        params["page"] = 1
        params["get_rid"] = "yes"
        params["submission_ids_only"] = "yes"

        while True:
            data = self._call("search", params)
            if not data["submissions"]:
                return

            yield from self.detail(data["submissions"])

            if data["page"] >= data["pages_count"]:
                return
            if "get_rid" in params:
                del params["get_rid"]
                params["rid"] = data["rid"]
            params["page"] += 1


@cache(maxage=365*86400, keyarg=1)
def _authenticate_impl(api, username, password):
    api.extractor.log.info("Logging in as %s", username)

    url = "https://inkbunny.net/api_login.php"
    data = {"username": username, "password": password}
    data = api.extractor.request(url, method="POST", data=data).json()

    if "sid" not in data:
        raise exception.AuthenticationError(data.get("error_message"))
    return data["sid"]
