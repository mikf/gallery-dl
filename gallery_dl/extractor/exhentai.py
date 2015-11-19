# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at http://exhentai.org/"""

from .common import Extractor, Message
from .. import config, text, iso639_1
import time
import random

info = {
    "category": "exhentai",
    "extractor": "ExhentaiExtractor",
    "directory": ["{category}", "{gallery-id}"],
    "filename": "{gallery-id}_{num:>04}_{imgkey}_{name}.{extension}",
    "pattern": [
        r"(?:https?://)?(g\.e-|ex)hentai\.org/g/(\d+)/([\da-f]{10})",
    ],
}

class ExhentaiExtractor(Extractor):

    api_url = "http://exhentai.org/api.php"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.version, self.gid, self.token = match.groups()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "http://exhentai.org/",
        })
        cookies = config.get(("extractor", "exhentai", "cookies"), {})
        for key, value in cookies.items():
            self.session.cookies.set(key, value, domain=".exhentai.org", path="/")
        self.wait_min = config.interpolate(("extractor", "exhentai", "wait-min"), 3)
        self.wait_max = config.interpolate(("extractor", "exhentai", "wait-max"), 6)
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min

    def items(self):
        yield Message.Version, 1
        page = self.request(self.url).text
        data, url = self.get_job_metadata(page)

        headers = self.session.headers.copy()
        headers["Accept"] = "image/png,image/*;q=0.8,*/*;q=0.5"
        yield Message.Headers, headers
        yield Message.Cookies, self.session.cookies
        yield Message.Directory, data

        urlkey = "url"
        if config.interpolate(("extractor", "exhentai", "download-original"), True):
            urlkey = "origurl"
        for num, image in enumerate(self.get_images(url), 1):
            image.update(data)
            image["num"] = num
            text.nameext_from_url(image["url"], image)
            if "/fullimg.php" in image[urlkey]:
                self.wait((1, 2))
            yield Message.Url, image[urlkey], image

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "category"     : info["category"],
            "gallery-id"   : self.gid,
            "gallery-token": self.token,
        }
        data, _ = text.extract_all(page, (
            ("title"   , '<h1 id="gn">', '</h1>'),
            ("title_jp", '<h1 id="gj">', '</h1>'),
            ("date"    , '>Posted:</td><td class="gdt2">', '</td>'),
            ("language", '>Language:</td><td class="gdt2">', '</td>'),
            ("size"    , '>File Size:</td><td class="gdt2">', ' '),
            ("count"   , '>Length:</td><td class="gdt2">', ' '),
            ("url"     , 'hentai.org/s/', '"'),
        ), values=data)
        pos = data["language"].find(" ")
        if pos != -1:
            data["language"] = data["language"][:pos]
        data["lang"] = iso639_1.language_to_code(data["language"])
        url = "http://exhentai.org/s/" + data["url"]
        del data["url"]
        return data, url

    def get_images(self, url):
        """Collect url and metadata for all images in this gallery"""
        self.wait()
        page = self.request(url).text
        data, pos = text.extract_all(page, (
            (None         , '<div id="i3"><a onclick="return load_image(', ''),
            ("imgkey-next", "'", "'"),
            ("url"        , '<img id="img" src="', '"'),
            ("title"      , '<div id="i4"><div>', ' :: '),
            ("origurl"    , 'http://exhentai.org/fullimg.php', '"'),
            ("gid"        , 'var gid=',  ';'),
            ("startkey"   , 'var startkey="', '";'),
            ("showkey"    , 'var showkey="', '";'),
        ))
        data["imgkey"] = data["startkey"]
        if data["origurl"]:
            data["origurl"] = "http://exhentai.org/fullimg.php" + text.unescape(data["origurl"])
        else:
            data["origurl"] = data["url"]
        yield data

        request = {
            "method" : "showpage",
            "page"   : 2,
            "gid"    : int(data["gid"]),
            "imgkey" : data["imgkey-next"],
            "showkey": data["showkey"],
        }
        while True:
            if data["imgkey"] == data["imgkey-next"]:
                return
            self.wait()
            page = self.session.post(self.api_url, json=request).json()
            data["imgkey"] = data["imgkey-next"]
            data["imgkey-next"], pos = text.extract(page["i3"], "'", "'")
            data["url"]        , pos = text.extract(page["i3"], '<img id="img" src="', '"', pos)
            data["title"]      , pos = text.extract(page["i" ], '<div>', ' :: ')
            data["origurl"]    , pos = text.extract(page["i7"], '<a href="', '"')
            if data["origurl"]:
                data["origurl"] = text.unescape(data["origurl"])
            else:
                data["origurl"] = data["url"]
            yield data
            request["imgkey"] = data["imgkey-next"]
            request["page"] += 1

    def wait(self, waittime=None):
        """Wait for a randomly chosen amount of seconds"""
        if not waittime:
            waittime = random.uniform(self.wait_min, self.wait_max)
        else:
            waittime = random.uniform(*waittime)
        time.sleep(waittime)
