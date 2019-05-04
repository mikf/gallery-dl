# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.sex.com/"""

from .common import Extractor, Message
from .. import text


class SexcomExtractor(Extractor):
    """Base class for sexcom extractors"""
    category = "sexcom"
    directory_fmt = ("{category}")
    filename_fmt = "{pin_id}{title:? //}.{extension}"
    archive_fmt = "{pin_id}"
    root = "https://www.sex.com"

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, self.metadata()
        for url in self.pins():
            pin = self._parse_pin(url)
            yield Message.Url, pin["url"], pin

    def metadata(self):
        return {}

    def pins(self):
        return ()

    def _pagination(self, url):
        while True:
            extr = text.extract_from(self.request(url).text)

            while True:
                href = extr('<a class="image_wrapper" href="', '"')
                if not href:
                    break
                yield self.root + href

            pager = extr('id="pagenum"', '</div>')
            url = text.extract(pager, ' href="', '"')[0]
            if not url:
                return
            url = text.urljoin(self.root, url)

    def _parse_pin(self, pin_url):
        extr = text.extract_from(self.request(pin_url).text)
        data = {}

        data["thumbnail"] = extr('itemprop="thumbnail" content="', '"')
        data["type"] = extr('<h1>' , '<').rstrip(" -").strip().lower()
        data["title"] = text.unescape(extr('itemprop="name">' , '<'))
        data["repins"] = text.parse_int(text.extract(
            extr('"btn-group"', '</div>'), '"btn btn-primary">' , '<')[0])
        data["likes"] = text.parse_int(text.extract(
            extr('"btn-group"', '</div>'), '"btn btn-default">' , '<')[0])
        data["pin_id"] = text.parse_int(extr('data-id="', '"'))

        if data["type"] == "video":
            info = extr("player.updateSrc(", ");")

            if info:
                path = text.extract(info, "src: '", "'")[0]
                data["filename"] = path.rpartition("/")[2]
                data["extension"] = "mp4"
                if "'HD'" in info:
                    path += "/hd"
                data["url"] = self.root + path
            else:
                data["url"] = "ytdl:" + text.extract(
                    extr('<iframe', '>'), ' src="', '"')[0]
        else:
            data["url"] = extr(' src="', '"')
            text.nameext_from_url(data["url"], data)

        data["uploader"] = extr('itemprop="author">', '<')
        data["date"] = extr('datetime="', '"')
        data["tags"] = text.split_html(extr('class="tags"> Tags', '</div>'))
        data["comments"] = text.parse_int(extr('Comments (', ')'))

        return data


class SexcomPinExtractor(SexcomExtractor):
    """Extractor a pinned image or video on www.sex.com"""
    subcategory = "pin"
    directory_fmt = ("{category}",)
    pattern = r"(?:https?://)?(?:www\.)?sex\.com/pin/(\d+)"
    test = (
        # picture
        ("https://www.sex.com/pin/56714360/", {
            "url": "599190d6e3d79f9f49dda194a0a58cb0ffa3ab86",
            "keyword": {
                "comments": int,
                "date": "2018-10-02T21:18:17-04:00",
                "extension": "jpg",
                "filename": "20037816",
                "likes": int,
                "pin_id": 56714360,
                "repins": int,
                "tags": list,
                "thumbnail": str,
                "title": "Pin #56714360",
                "type": "picture",
                "uploader": "alguem",
                "url": str,
            },
        }),
        # gif
        ("https://www.sex.com/pin/11465040-big-titted-hentai-gif/", {
            "url": "98a82c5ae7a65c8228e1405ac740f80d4d556de1",
        }),
        # video
        ("https://www.sex.com/pin/55748381/", {
            "pattern": "https://www.sex.com/video/stream/776238/hd",
        }),
        # pornhub embed
        ("https://www.sex.com/pin/55847384-very-nicely-animated/", {
            "pattern": "ytdl:https://www.pornhub.com/embed/ph56ef24b6750f2",
        }),
    )

    def __init__(self, match):
        SexcomExtractor.__init__(self, match)
        self.pin_id = match.group(1)

    def pins(self):
        return ("{}/pin/{}/".format(self.root, self.pin_id),)


class SexcomBoardExtractor(SexcomExtractor):
    """Extractor for pins from a board on www.sex.com"""
    subcategory = "board"
    directory_fmt = ("{category}", "{user}", "{board}")
    pattern = (r"(?:https?://)?(?:www\.)?sex\.com/user"
               r"/([^/?&#]+)/(?!(?:following|pins|repins|likes)/)([^/?&#]+)")
    test = ("https://www.sex.com/user/ronin17/exciting-hentai/", {
        "count": ">= 15",
    })

    def __init__(self, match):
        SexcomExtractor.__init__(self, match)
        self.user, self.board = match.groups()

    def metadata(self):
        return {
            "user" : text.unquote(self.user),
            "board": text.unquote(self.board),
        }

    def pins(self):
        url = "{}/user/{}/{}/".format(self.root, self.user, self.board)
        return self._pagination(url)


class SexcomSearchExtractor(SexcomExtractor):
    """Extractor for search results on www.sex.com"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search[query]}")
    pattern = (r"(?:https?://)?(?:www\.)?sex\.com/((?:"
               r"(pic|gif|video)s/([^/?&#]+)|search/(pic|gif|video)s"
               r")/?(?:\?([^#]+))?)")
    test = (
        ("https://www.sex.com/search/pics?query=ecchi", {
            "range": "1-10",
            "count": 10,
        }),
        ("https://www.sex.com/videos/hentai/", {
            "range": "1-10",
            "count": 10,
        }),
    )

    def __init__(self, match):
        SexcomExtractor.__init__(self, match)
        self.path = match.group(1)

        self.search = text.parse_query(match.group(5))
        self.search["type"] = match.group(2) or match.group(4)
        if "query" not in self.search:
            self.search["query"] = match.group(3) or ""

    def metadata(self):
        return {"search": self.search}

    def pins(self):
        url = "{}/{}".format(self.root, self.path)
        return self._pagination(url)
