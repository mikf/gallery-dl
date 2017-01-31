# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and ugoira from http://www.pixiv.net/"""

from .common import Extractor, Message
from .. import config, text, exception
from ..cache import cache
import re
import json


class PixivUserExtractor(Extractor):
    """Extractor for works of a pixiv-user"""
    category = "pixiv"
    subcategory = "user"
    directory_fmt = ["{category}", "{artist-id}-{artist-nick}"]
    filename_fmt = "{category}_{artist-id}_{id}{num}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?pixiv\.net/"
               r"member(?:_illust)?\.php\?id=(\d+)"]
    test = [
        ("http://www.pixiv.net/member_illust.php?id=173530", {
            "url": "8f2fc0437e2095ab750c4340a4eba33ec6269477",
        }),
        ("http://www.pixiv.net/member_illust.php?id=173531", {
            "exception": exception.NotFoundError,
        }),
    ]
    member_url = "http://www.pixiv.net/member_illust.php"
    illust_url = "http://www.pixiv.net/member_illust.php?mode=medium"

    def __init__(self, match):
        Extractor.__init__(self)
        self.artist_id = match.group(1)
        self.api = PixivAPI(self.session)
        self.api_call = self.api.user_works
        self.load_ugoira = config.interpolate(
            ("extractor", "pixiv", "ugoira"), True
        )

    def items(self):
        metadata = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Headers, self.session.headers
        yield Message.Cookies, self.session.cookies
        yield Message.Directory, metadata

        for work in self.get_works():
            pos = work["extension"].rfind("?", -18)
            if pos != -1:
                timestamp = work["extension"][pos:]
                work["extension"] = work["extension"][:pos]
            else:
                timestamp = ""

            if work["type"] == "ugoira":
                if not self.load_ugoira:
                    continue
                url, framelist = self.parse_ugoira(work)
                work["extension"] = "zip"
                yield Message.Url, url, work
                work["extension"] = "txt"
                yield Message.Url, "text://"+framelist, work

            elif work["page_count"] == 1:
                yield Message.Url, work["url"], work

            else:
                url = work["url"]
                ext = work["extension"]
                off = url.rfind(".")
                if url[off-2] == "p":
                    off -= 3
                if work["id"] > 11319935 and "/img-original/" not in url:
                    big = "_big"
                else:
                    big = ""
                for i in range(work["page_count"]):
                    work["num"] = "_p{:02}".format(i)
                    url = "{}{}_p{}.{}{}".format(
                        url[:off], big, i, ext, timestamp
                    )
                    yield Message.Url, url, work

    def get_works(self):
        """Yield all work-items for a pixiv-member"""
        pagenum = 1
        while True:
            data = self.api_call(self.artist_id, pagenum)
            for work in data["response"]:
                yield self.prepare_work(work)
            pinfo = data["pagination"]
            if pinfo["current"] == pinfo["pages"]:
                return
            pagenum = pinfo["next"]

    def prepare_work(self, work):
        """Prepare a work-dictionary with additional keywords"""
        user = work["user"]
        url = work["image_urls"]["large"]
        work["artist-id"] = user["id"]
        work["artist-name"] = user["name"]
        work["artist-nick"] = user["account"]
        work["num"] = ""
        work["url"] = url
        work["extension"] = url[url.rfind(".")+1:]
        return work

    def parse_ugoira(self, data):
        """Parse ugoira data"""
        # get illust page
        page = self.request(
            self.illust_url, params={"illust_id": data["id"]},
        ).text

        # parse page
        frames, _ = text.extract(page, ',"frames":[', ']')

        # build url
        url = re.sub(
            r"/img-original/(.+/\d+)[^/]+",
            r"/img-zip-ugoira/\g<1>_ugoira1920x1080.zip",
            data["url"]
        )

        # build framelist
        framelist = re.sub(
            r'\{"file":"([^"]+)","delay":(\d+)\},?',
            r'\1 \2\n', frames
        )
        return url, framelist

    def get_job_metadata(self, user=None):
        """Collect metadata for extractor-job"""
        if not user:
            user = self.api.user(self.artist_id)["response"][0]
        return {
            "artist-id": user["id"],
            "artist-name": user["name"],
            "artist-nick": user["account"],
        }


class PixivWorkExtractor(PixivUserExtractor):
    """Extractor for a single pixiv work/illustration"""
    subcategory = "work"
    pattern = [(r"(?:https?://)?(?:www\.)?pixiv\.net/member(?:_illust)?\.php"
                r"\?(?:[^&]+&)*illust_id=(\d+)"),
               (r"(?:https?://)?i\d+\.pixiv\.net(?:/.*)?/img-[^/]+/img"
                r"/\d{4}(?:/\d\d){5}/(\d+)"),
               (r"(?:https?://)?img\d+\.pixiv\.net/img/[^/]+/(\d+)")]
    test = [
        (("http://www.pixiv.net/member_illust.php"
          "?mode=medium&illust_id=966412"), {
            "url": "efb622f065b0871e92195e7bee0b4d75bd687d8d",
            "content": "69a8edfb717400d1c2e146ab2b30d2c235440c5a",
        }),
        (("http://www.pixiv.net/member_illust.php"
          "?mode=medium&illust_id=966411"), {
            "exception": exception.NotFoundError,
        }),
        (("http://i1.pixiv.net/c/600x600/img-master/"
          "img/2008/06/13/00/29/13/966412_p0_master1200.jpg"), {
            "url": "efb622f065b0871e92195e7bee0b4d75bd687d8d",
        }),
    ]

    def __init__(self, match):
        PixivUserExtractor.__init__(self, match)
        self.illust_id = match.group(1)
        self.load_ugoira = True
        self.work = None

    def get_works(self):
        return (self.prepare_work(self.work),)

    def get_job_metadata(self, user=None):
        """Collect metadata for extractor-job"""
        self.work = self.api.work(self.illust_id)["response"][0]
        return PixivUserExtractor.get_job_metadata(self, self.work["user"])


class PixivFavoriteExtractor(PixivUserExtractor):
    """Extractor for all favorites/bookmarks of a pixiv-user"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "bookmarks", "{artist-id}-{artist-nick}"]
    pattern = [r"(?:https?://)?(?:www\.)?pixiv\.net/bookmark\.php\?id=(\d+)"]
    test = [("http://www.pixiv.net/bookmark.php?id=173530", {
        "url": "0110c5c2ee9612a0362e26f7481a8916b6f410fe",
    })]

    def __init__(self, match):
        PixivUserExtractor.__init__(self, match)
        self.api_call = self.api.user_favorite_works

    def prepare_work(self, work):
        return PixivUserExtractor.prepare_work(self, work["work"])


class PixivBookmarkExtractor(PixivFavoriteExtractor):
    """Extractor for all favorites/bookmarks of your own account"""
    subcategory = "bookmark"
    pattern = [r"(?:https?://)?(?:www\.)?pixiv\.net/bookmark\.php()$"]
    test = []

    def __init__(self, match):
        PixivFavoriteExtractor.__init__(self, match)
        self.api.login()
        self.artist_id = self.api.user_id


def require_login(func):
    """Decorator: auto-login before api-calls"""
    def wrap(self, *args):
        self.login()
        return func(self, *args)
    return wrap


class PixivAPI():
    """Minimal interface for the Pixiv Public-API for mobile devices

    For a better and more complete implementation, see
    - https://github.com/upbit/pixivpy
    For in-depth information regarding the Pixiv Public-API, see
    - http://blog.imaou.com/opensource/2014/10/09/pixiv_api_for_ios_update.html
    """
    def __init__(self, session):
        self.session = session
        self.session.headers.update({
            "Referer": "http://www.pixiv.net/",
            "User-Agent": "PixivIOSApp/5.8.0",
        })
        self.user_id = -1

    @require_login
    def user(self, user_id):
        """Query information about a pixiv user"""
        response = self.session.get(
            "https://public-api.secure.pixiv.net/v1/users/"
            "{user}.json".format(user=user_id)
        )
        return self._parse(response)

    @require_login
    def work(self, illust_id):
        """Query information about a single pixiv work/illustration"""
        params = {
            "image_sizes": "large",
        }
        response = self.session.get(
            "https://public-api.secure.pixiv.net/v1/works/"
            "{illust}.json".format(illust=illust_id), params=params
        )
        return self._parse(response)

    @require_login
    def user_works(self, user_id, page, per_page=20):
        """Query information about the works of a pixiv user"""
        params = {
            "page": page,
            "per_page": per_page,
            "image_sizes": "large",
        }
        response = self.session.get(
            "https://public-api.secure.pixiv.net/v1/users/"
            "{user}/works.json".format(user=user_id), params=params
        )
        return self._parse(response)

    @require_login
    def user_favorite_works(self, user_id, page, per_page=20):
        """Query information about the favorites works of a pixiv user"""
        params = {
            "page": page,
            "per_page": per_page,
            "include_stats": False,
            "image_sizes": "large",
        }
        response = self.session.get(
            "https://public-api.secure.pixiv.net/v1/users/"
            "{user}/favorite_works.json".format(user=user_id), params=params
        )
        return self._parse(response)

    def login(self):
        """Login and gain a Pixiv Public-API access token"""
        username = config.interpolate(("extractor", "pixiv", "username"))
        password = config.interpolate(("extractor", "pixiv", "password"))
        self.user_id, auth_header = self._login_impl(username, password)
        self.session.headers["Authorization"] = auth_header

    @cache(maxage=50*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        data = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": "bYGKuGVw91e0NMfPGp44euvGt59s",
            "client_secret": "HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK",
        }
        response = self.session.post(
            "https://oauth.secure.pixiv.net/auth/token", data=data
        )
        if response.status_code not in (200, 301, 302):
            raise exception.AuthenticationError()
        try:
            response = self._parse(response)["response"]
            token = response["access_token"]
            user = response["user"]["id"]
        except:
            raise Exception("Get access_token error! Response: %s" % (token))
        return user, "Bearer " + token

    @staticmethod
    def _parse(response, empty=[None]):
        """Parse a Pixiv Public-API response"""
        data = json.loads(response.text)
        status = data.get("status")
        response = data.get("response", empty)
        if status == "failure" or response == empty:
            raise exception.NotFoundError()
        return data
