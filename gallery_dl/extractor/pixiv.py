# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and ugoira from http://www.pixiv.net/"""

from .common import Extractor, Message
from .. import config, text
import re
import json
import time

class PixivUserExtractor(Extractor):
    """Extract all works of a single pixiv-user"""

    category = "pixiv"
    directory_fmt = ["{category}", "{artist-id}-{artist-nick}"]
    filename_fmt = "{category}_{artist-id}_{id}{num}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?pixiv\.net/member(?:_illust)?\.php\?id=(\d+)"]
    member_url = "http://www.pixiv.net/member_illust.php"
    illust_url = "http://www.pixiv.net/member_illust.php?mode=medium"

    def __init__(self, match):
        Extractor.__init__(self)
        self.artist_id = match.group(1)
        self.api = PixivAPI(self.session)

    def items(self):
        metadata = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Headers, self.session.headers
        yield Message.Cookies, self.session.cookies
        yield Message.Directory, metadata

        for work in self.get_works():
            work.update(metadata)

            pos = work["extension"].rfind("?", -18)
            if pos != -1:
                timestamp = work["extension"][pos:]
                work["extension"] = work["extension"][:pos]
            else:
                timestamp = ""

            if work["type"] == "ugoira":
                url, framelist = self.parse_ugoira(work)
                work["extension"] = "zip"
                yield Message.Url, url, work.copy()
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
                    url = "{}{}_p{}.{}{}".format(url[:off], big, i, ext, timestamp)
                    yield Message.Url, url, work.copy()

    def get_works(self):
        """Yield all work-items for a pixiv-member"""
        pagenum = 1
        while True:
            data = self.api.user_works(self.artist_id, pagenum)
            for work in data["response"]:
                url = work["image_urls"]["large"]
                work["num"] = ""
                work["url"] = url
                work["extension"] = url[url.rfind(".")+1:]
                yield work
            pinfo = data["pagination"]
            if pinfo["current"] == pinfo["pages"]:
                return
            pagenum = pinfo["next"]

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

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        data = self.api.user(self.artist_id)["response"][0]
        return {
            "category": self.category,
            "artist-id": self.artist_id,
            "artist-name": data["name"],
            "artist-nick": data["account"],
        }


class PixivWorkExtractor(PixivUserExtractor):
    """Extract a single pixiv work/illustration"""

    pattern = [(r"(?:https?://)?(?:www\.)?pixiv\.net/member(?:_illust)?\.php"
                r"\?(?:[^&]+&)*illust_id=(\d+)")]

    def __init__(self, match):
        PixivUserExtractor.__init__(self, match)
        self.illust_id = match.group(1)
        self.work = None

    def get_works(self):
        url = self.work["image_urls"]["large"]
        self.work["num"] = ""
        self.work["url"] = url
        self.work["extension"] = url[url.rfind(".")+1:]
        return (self.work,)

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        self.work = self.api.work(self.illust_id)["response"][0]
        self.artist_id = self.work["user"]["id"]
        return PixivUserExtractor.get_job_metadata(self)


def require_login(func):
    """Decorator: auto-login before api-calls"""
    def wrap(self, *args):
        now = time.time()
        if now - self.last_login > PixivAPI.token_timeout:
            self.login()
            self.last_login = now
        return func(self, *args)
    return wrap

class PixivAPI():
    """Minimal interface for the Pixiv Public-API for mobile devices

    For a better and more complete implementation, see
    - https://github.com/upbit/pixivpy
    For in-depth information regarding the Pixiv Public-API, see
    - http://blog.imaou.com/opensource/2014/10/09/pixiv_api_for_ios_update.html
    """

    token_timeout = 50*60 # 50 minutes

    def __init__(self, session):
        self.last_login = 0
        self.session = session
        self.session.headers.update({
            "Referer": "http://www.pixiv.net/",
            "User-Agent": "PixivIOSApp/5.8.0",
        })
        config.setdefault(("extractor", "pixiv"), {})

    def login(self):
        """Login and gain a Pixiv Public-API access token"""
        pconf = config.get(("extractor", "pixiv"))
        token = pconf.get("access-token")
        now = time.time()
        if token:
            timestamp = pconf.get("access-token-timestamp", 0)
            if now - timestamp > PixivAPI.token_timeout:
                token = None
        if not token:
            data = {
                "username": pconf.get("username"),
                "password": pconf.get("password"),
                "grant_type": "password",
                "client_id": "bYGKuGVw91e0NMfPGp44euvGt59s",
                "client_secret": "HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK",
            }
            response = self.session.post(
                "https://oauth.secure.pixiv.net/auth/token", data=data
            )
            if response.status_code not in (200, 301, 302):
                raise Exception("login() failed! check username and password.\n"
                                "HTTP %s: %s" % (response.status_code, response.text))
            try:
                token = self._parse(response)["response"]["access_token"]
            except:
                raise Exception("Get access_token error! Response: %s" % (token))
            pconf["access-token"] = token
            pconf["access-token-timestamp"] = now - 1
        self.session.headers["Authorization"] = (
            "Bearer " + token
        )

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
            'image_sizes': 'large',
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
            'page': page,
            'per_page': per_page,
            'image_sizes': 'large',
        }
        response = self.session.get(
            "https://public-api.secure.pixiv.net/v1/users/"
            "{user}/works.json".format(user=user_id), params=params
        )
        return self._parse(response)

    @staticmethod
    def _parse(response):
        """Parse a Pixiv Public-API response"""
        return json.loads(response.text)
