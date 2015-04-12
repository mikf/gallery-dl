# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and ugoira from http://www.pixiv.net/"""

from .common import AsynchronousExtractor
from .common import Message
from .common import safe_request
import re
import csv
import requests

info = {
    "category": "pixiv",
    "extractor": "PixivExtractor",
    "directory": ["{category}", "{artist-id}"],
    "filename": "{category}_{artist-id}_{illust-id}{num}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?pixiv\.net/member(?:_illust)?\.php\?id=(\d+)",
    ],
}


class PixivExtractor(AsynchronousExtractor):

    member_url = "http://www.pixiv.net/member_illust.php"
    illust_url = "http://www.pixiv.net/member_illust.php?mode=medium"

    singl_v1_fmt = ("http://i{thumbnail-url[8]}.pixiv.net/img{directory:>02}"
                    "/img/{artist-nick}/{illust-id}.{extension}")
    manga_v1_fmt = ("http://i{thumbnail-url[8]}.pixiv.net/img{directory:>02}"
                    "/img/{artist-nick}/{illust-id}{big}_p{index}.{extension}")

    singl_v2_fmt = ("http://i{thumbnail-url[8]}.pixiv.net/img-original/img"
                    "/{url-date}/{illust-id}_p0.{extension}")
    manga_v2_fmt = ("http://i{thumbnail-url[8]}.pixiv.net/img-original/img"
                    "/{url-date}/{illust-id}_p{index}.{extension}")

    def __init__(self, match, config):
        AsynchronousExtractor.__init__(self, config)
        self.config = config
        self.artist_id = match.group(1)
        self.api = PixivAPI(config["pixiv-cookies"]["PHPSESSID"])
        self.session.headers.update({"Referer": "http://www.pixiv.net/"})
        self.session.cookies.update(self.config["pixiv-cookies"])

    def items(self):
        yield Message.Version, 1
        yield Message.Headers, self.session.headers
        yield Message.Cookies, self.session.cookies
        yield Message.Directory, self.get_job_metadata()

        for illust_id in self.get_illust_ids():
            data = self.api.request(illust_id)
            # debug
            # for i, value in enumerate(data):
                # print("{:02}: {}".format(i, value))
            # return
            # debug end

            # if "うごイラ" in data["tags"]:
                # ugoira / animations
                    # url, framelist = self.parse_ugoira(img)
                    # data[2] = "zip"
                    # yield (url, sname_fmt.format(*data))
                    # data[2] = "txt"
                    # yield (framelist, sname_fmt.format(*data))
                    # continue

            # images
            if illust_id > 46270949:
                big = ""
                url_s_fmt = self.singl_v2_fmt
                url_m_fmt = self.manga_v2_fmt
            else:
                big = "_big" if illust_id > 11319935 else ""
                url_s_fmt = self.singl_v1_fmt
                url_m_fmt = self.manga_v1_fmt

            if not data["count"]:
                yield Message.Url, url_s_fmt.format(**data), data
            else:
                for i in range(0, int(data["count"])):
                    data["num"] = "_p{:02}".format(i)
                    yield (Message.Url,
                           url_m_fmt.format(index=i, big=big, **data),
                           data.copy())

    def get_illust_ids(self):
        """Yield all illust-ids for a pixiv-member"""
        needle = ('<li class="image-item "><a href="'
                  '/member_illust.php?mode=medium&amp;illust_id=')
        params = {"id": self.artist_id, "p": 1}
        while True:
            text = self.request(self.member_url, params=params).text
            pos = 0
            found = 0
            while True:
                illust_id, pos = self.extract(text, needle, '"', pos)
                if illust_id is None:
                    break
                found += 1
                yield int(illust_id)
            if found != 20:
                return
            params["p"] += 1


    def parse_ugoira(self, illust_id):
        """Parse ugoira data"""
        # get illust page
        text = self.request(
            self.illust_url,
            params={"illust_id": illust_id},
        ).text

        # parse page
        url   , pos = self.extract(text, 'ugokuIllustFullscreenData  = {"src":"', '"')
        frames, pos = self.extract(text, '"frames":[', ']', pos)

        # fix url
        url = url.replace("\\/", "/")

        # build framelist
        framelist = "text://" + re.sub(
            r'\{"file":"([^"]+)","delay":(\d+)\},?',
            r'\1 \2\n',
            frames
        )
        return url, framelist

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": info["category"],
            "artist-id": self.artist_id,
        }


class PixivAPI():
    api_url = "http://spapi.pixiv.net/iphone/illust.php"

    def __init__(self, session_id):
        self.session = requests.Session()
        self.session.params["PHPSESSID"] = session_id

    def request(self, illust_id):
        data = next(csv.reader(
            [self.api_call(illust_id)]
        ))
        return {
            "category": info["category"],
            "illust-id": data[0],
            "artist-id": data[1],
            "extension": data[2],
            "title": data[3],
            "directory": data[4],
            "artist-name": data[5],
            "thumbnail-url": data[6],
            "url-date": data[6][45:64],
            # "thumbnail-mobile-url": data[9],
            "date": data[12],
            "tags": data[13],
            # "description": data[18],
            "count": data[19],
            "artist-nick": data[24],
            # "artist-avatar-url": data[29],
            "num": "",
        }

    def api_call(self, illust_id):
        text = ""
        while len(text) < 32:
            text = safe_request(
                self.session, self.api_url,
                params={"illust_id": illust_id}
            ).text
        return text
