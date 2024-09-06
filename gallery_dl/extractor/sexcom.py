# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
        yield Message.Directory, self.metadata()
        for pin in map(self._parse_pin, self.pins()):
            if pin:
                yield Message.Url, pin["url"], pin

    def metadata(self):
        return {}

    def pins(self):
        return ()

    def _pagination(self, url):
        while True:
            extr = text.extract_from(self.request(url).text)
            url = extr('<link rel="next" href="', '"')

            while True:
                href = extr('<a class="image_wrapper" href="', '"')
                if not href:
                    break
                yield self.root + href

            if not url:
                return
            url = text.urljoin(self.root, text.unescape(url))

    def _parse_pin(self, url):
        response = self.request(url, fatal=False)
        if response.status_code >= 400:
            self.log.warning('Unable to fetch %s ("%s %s")',
                             url, response.status_code, response.reason)
            return None
        extr = text.extract_from(response.text)
        data = {}

        data["_http_headers"] = {"Referer": url}
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
                try:
                    path, _ = text.rextract(
                        info, "src: '", "'", info.index("label: 'HD'"))
                except ValueError:
                    path = text.extr(info, "src: '", "'")
                text.nameext_from_url(path, data)
                data["url"] = path
            else:
                iframe = extr('<iframe', '>')
                src = (text.extr(iframe, ' src="', '"') or
                       text.extr(iframe, " src='", "'"))
                if not src:
                    self.log.warning("Unable to fetch media from %s", url)
                    return None
                data["extension"] = None
                data["url"] = "ytdl:" + src
        else:
            data["_http_validate"] = _check_empty
            url = text.unescape(extr(' src="', '"'))
            data["url"] = url.partition("?")[0]
            data["_fallback"] = (url,)
            text.nameext_from_url(data["url"], data)

        data["uploader"] = extr('itemprop="author">', '<')
        data["date"] = text.parse_datetime(extr('datetime="', '"'))
        data["tags"] = text.split_html(extr('class="tags"> Tags', '</div>'))
        data["comments"] = text.parse_int(extr('Comments (', ')'))

        return data


class SexcomPinExtractor(SexcomExtractor):
    """Extractor for a pinned image or video on www.sex.com"""
    subcategory = "pin"
    directory_fmt = ("{category}",)
    pattern = r"(?:https?://)?(?:www\.)?sex\.com/pin/(\d+)(?!.*#related$)"
    example = "https://www.sex.com/pin/12345-TITLE/"

    def __init__(self, match):
        SexcomExtractor.__init__(self, match)
        self.pin_id = match.group(1)

    def pins(self):
        return ("{}/pin/{}/".format(self.root, self.pin_id),)


class SexcomRelatedPinExtractor(SexcomPinExtractor):
    """Extractor for related pins on www.sex.com"""
    subcategory = "related-pin"
    directory_fmt = ("{category}", "related {original_pin[pin_id]}")
    pattern = r"(?:https?://)?(?:www\.)?sex\.com/pin/(\d+).*#related$"
    example = "https://www.sex.com/pin/12345#related"

    def metadata(self):
        pin = self._parse_pin(SexcomPinExtractor.pins(self)[0])
        return {"original_pin": pin}

    def pins(self):
        url = "{}/pin/related?pinId={}&limit=24&offset=0".format(
            self.root, self.pin_id)
        return self._pagination(url)


class SexcomPinsExtractor(SexcomExtractor):
    """Extractor for a user's pins on www.sex.com"""
    subcategory = "pins"
    directory_fmt = ("{category}", "{user}")
    pattern = r"(?:https?://)?(?:www\.)?sex\.com/user/([^/?#]+)/pins/"
    example = "https://www.sex.com/user/USER/pins/"

    def __init__(self, match):
        SexcomExtractor.__init__(self, match)
        self.user = match.group(1)

    def metadata(self):
        return {"user": text.unquote(self.user)}

    def pins(self):
        url = "{}/user/{}/pins/".format(self.root, self.user)
        return self._pagination(url)


class SexcomLikesExtractor(SexcomExtractor):
    """Extractor for a user's liked pins on www.sex.com"""
    subcategory = "likes"
    directory_fmt = ("{category}", "{user}", "Likes")
    pattern = r"(?:https?://)?(?:www\.)?sex\.com/user/([^/?#]+)/likes/"
    example = "https://www.sex.com/user/USER/likes/"

    def __init__(self, match):
        SexcomExtractor.__init__(self, match)
        self.user = match.group(1)

    def metadata(self):
        return {"user": text.unquote(self.user)}

    def pins(self):
        url = "{}/user/{}/likes/".format(self.root, self.user)
        return self._pagination(url)


class SexcomBoardExtractor(SexcomExtractor):
    """Extractor for pins from a board on www.sex.com"""
    subcategory = "board"
    directory_fmt = ("{category}", "{user}", "{board}")
    pattern = (r"(?:https?://)?(?:www\.)?sex\.com/user"
               r"/([^/?#]+)/(?!(?:following|pins|repins|likes)/)([^/?#]+)")
    example = "https://www.sex.com/user/USER/BOARD/"

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
               r"(pic|gif|video)s/([^/?#]*)|search/(pic|gif|video)s"
               r")/?(?:\?([^#]+))?)")
    example = "https://www.sex.com/search/pics?query=QUERY"

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


def _check_empty(response):
    return response.headers.get("content-length") != "0"
