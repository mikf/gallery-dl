# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
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
    directory_fmt = ("{category}", "{post[username]!l}")
    filename_fmt = "{post[submission_id]} {file_id} {post[title]}.{extension}"
    archive_fmt = "{file_id}"
    root = "https://inkbunny.net"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)

    def items(self):
        to_bool = ("deleted", "digitalsales", "favorite", "forsale",
                   "friends_only", "guest_block", "hidden", "printsales",
                   "public", "scraps")

        for post in self.posts():
            post["date"] = text.parse_datetime(
                post["create_datetime"] + "00", "%Y-%m-%d %H:%M:%S.%f%z")
            post["tags"] = [kw["keyword_name"] for kw in post["keywords"]]
            files = post["files"]

            for key in to_bool:
                post[key] = (post[key] == "t")

            del post["keywords"]
            del post["files"]

            yield Message.Directory, {"post": post}
            for file in files:
                file["post"] = post
                file["deleted"] = (file["deleted"] == "t")
                file["date"] = text.parse_datetime(
                    file["create_datetime"] + "00", "%Y-%m-%d %H:%M:%S.%f%z")
                text.nameext_from_url(file["file_name"], file)
                yield Message.Url, file["file_url_full"], file


class InkbunnyUserExtractor(InkbunnyExtractor):
    """Extractor for inkbunny user profile"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!s/)([^/?&#]+)"
    test = ("https://inkbunny.net/soina", {
        "pattern": r"https://[\w.]+\.metapix\.net/files/full/\d+/\d+_soina_.+",
        "range": "20-50",
        "keyword": {
            "date": "type:datetime",
            "deleted": bool,
            "file_id": "re:[0-9]+",
            "filename": r"re:[0-9]+_soina_\w+",
            "full_file_md5": "re:[0-9a-f]{32}",
            "mimetype": str,
            "submission_file_order": "re:[0-9]+",
            "submission_id": "re:[0-9]+",
            "user_id": "20969",
            "post": {
                "comments_count": "re:[0-9]+",
                "date": "type:datetime",
                "deleted": bool,
                "digitalsales": bool,
                "favorite": bool,
                "favorites_count": "re:[0-9]+",
                "forsale": bool,
                "friends_only": bool,
                "guest_block": bool,
                "hidden": bool,
                "pagecount": "re:[0-9]+",
                "pools": list,
                "pools_count": int,
                "printsales": bool,
                "public": bool,
                "rating_id": "re:[0-9]+",
                "rating_name": str,
                "ratings": list,
                "scraps": bool,
                "submission_id": "re:[0-9]+",
                "tags": list,
                "title": str,
                "type_name": str,
                "user_id": "20969",
                "username": "soina",
                "views": str,
            },
        },
    })

    def posts(self):
        api = InkbunnyAPI(self)
        return api.search(username=self.item)


class InkbunnyPostExtractor(InkbunnyExtractor):
    """Extractor for individual Inkbunny posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/s/(\d+)"
    test = (
        ("https://inkbunny.net/s/1829715", {
            "pattern": r"https://[\w.]+\.metapix\.net/files/full"
                       r"/2626/2626843_soina_dscn2296\.jpg",
            "content": "cf69d8dddf0822a12b4eef1f4b2258bd600b36c8",
        }),
        ("https://inkbunny.net/s/2044094", {
            "count": 4,
        }),
    )

    def posts(self):
        api = InkbunnyAPI(self)
        return api.detail(self.item)


class InkbunnyAPI():
    """Interface for the Inkunny API

    Ref: https://wiki.inkbunny.net/wiki/API
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.session_id = None

    def detail(self, submission_ids):
        """Get full details about submissions with the given IDs"""
        params = {"submission_ids": submission_ids}
        return self._call("submissions", params)["submissions"]

    def search(self, username):
        """Perform a search"""
        params = {"username": username}
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
        if not self.session_id:
            self.authenticate()

        url = "https://inkbunny.net/api_" + endpoint + ".php"
        params["sid"] = self.session_id
        data = self.extractor.request(url, params=params).json()

        if "error_code" in data:
            if str(data["error_code"]) == "2":
                self.authenticate(invalidate=True)
                return self._call(endpoint, params)
            raise exception.StopExtraction(data.get("error_message"))

        return data

    def _pagination_search(self, params):
        params["get_rid"] = "yes"
        params["submission_ids_only"] = "yes"

        while True:
            data = self._call("search", params)
            yield from self.detail(
                ",".join(s["submission_id"] for s in data["submissions"]))

            if data["page"] >= data["pages_count"]:
                return
            if "get_rid" in params:
                del params["get_rid"]
                params["rid"] = data["rid"]
                params["page"] = 2
            else:
                params["page"] += 1


@cache(maxage=360*24*3600, keyarg=1)
def _authenticate_impl(api, username, password):
    api.extractor.log.info("Logging in as %s", username)

    url = "https://inkbunny.net/api_login.php"
    data = {"username": username, "password": password}
    data = api.extractor.request(url, method="POST", data=data).json()

    if "sid" not in data:
        raise exception.AuthenticationError(data.get("error_message"))
    return data["sid"]
