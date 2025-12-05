# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.sex.com/"""

from .common import Extractor, Message
from .. import text, dt

BASE_PATTERN = r"(?:https?://)?(?:www\.)?sex\.com(?:/[a-z]{2})?"


class SexcomExtractor(Extractor):
    """Base class for sexcom extractors"""
    category = "sexcom"
    directory_fmt = ("{category}")
    filename_fmt = "{pin_id}{title:? //}.{extension}"
    archive_fmt = "{pin_id}"
    root = "https://www.sex.com"

    def items(self):
        self.gifs = self.config("gifs", True)

        yield Message.Directory, "", self.metadata()
        for pin in map(self._parse_pin, self.pins()):
            if not pin:
                continue

            url = pin["url"]
            parts = url.rsplit("/", 4)
            try:
                pin["date_url"] = d = dt.datetime(
                    int(parts[1]), int(parts[2]), int(parts[3]))
                if "date" not in pin:
                    pin["date"] = d
            except Exception:
                pass
            pin["tags"] = [t[1:] for t in pin["tags"]]

            yield Message.Url, url, pin

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
        if "/pin/" in url:
            if url[-1] != "/":
                url += "/"
        elif url[-1] == "/":
            url = url[:-1]

        response = self.request(url, fatal=False, allow_redirects=False)
        location = response.headers.get("location")

        if location:
            if location[0] == "/":
                location = self.root + location
            if len(location) <= 25:
                return self.log.warning(
                    'Unable to fetch %s: Redirect to homepage', url)
            response = self.request(location, fatal=False)

        if response.status_code >= 400:
            return self.log.warning('Unable to fetch %s: %s %s',
                                    url, response.status_code, response.reason)

        if "/pin/" in response.url:
            return self._parse_pin_legacy(response)
        if "/videos/" in response.url:
            return self._parse_pin_video(response)
        return self._parse_pin_image(response)

    def _parse_pin_legacy(self, response):
        extr = text.extract_from(response.text)
        data = {}

        data["_http_headers"] = {"Referer": response.url}
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
                    path = text.rextr(
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
                    self.log.warning(
                        "Unable to fetch media from %s", response.url)
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
        data["date"] = dt.parse_iso(extr('datetime="', '"'))
        data["tags"] = text.split_html(extr('class="tags"> Tags', '</div>'))
        data["comments"] = text.parse_int(extr('Comments (', ')'))

        return data

    def _parse_pin_image(self, response):
        extr = text.extract_from(response.text)
        href = extr(' href="', '"').partition("?")[0]
        title, _, type = extr("<title>", " | ").rpartition(" ")

        data = {
            "_http_headers": {"Referer": response.url},
            "url": href,
            "title": text.unescape(title),
            "pin_id": text.parse_int(extr(
                'rel="canonical" href="', '"').rpartition("/")[2]),
            "tags": text.split_html(extr("</h1>", "</section>")),
        }

        text.nameext_from_url(href, data)
        if type.lower() == "pic":
            data["type"] = "picture"
        else:
            data["type"] = "gif"
            if self.gifs and data["extension"] == "webp":
                data["extension"] = "gif"
                data["_fallback"] = (href,)
                data["url"] = href[:-4] + "gif"

        return data

    def _parse_pin_video(self, response):
        extr = text.extract_from(response.text)

        if not self.cookies.get("CloudFront-Key-Pair-Id", domain=".sex.com"):
            self.log.warning("CloudFront cookies required for video downloads")

        data = {
            "_ytdl_manifest": "hls",
            "_ytdl_manifest_headers": {"Referer": response.url},
            "extension": "mp4",
            "type": "video",
            "title": text.unescape(extr("<title>", " | Sex.com<")),
            "pin_id": text.parse_int(extr(
                'rel="canonical" href="', '"').rpartition("/")[2]),
            "tags": text.split_html(extr(
                'event_name="video_tags_click"', "<div data-testid=")
                .partition(">")[2]),
            "url": "ytdl:" + extr('<source src="', '"'),
        }

        return data


class SexcomPinExtractor(SexcomExtractor):
    """Extractor for a pinned image or video on www.sex.com"""
    subcategory = "pin"
    directory_fmt = ("{category}",)
    pattern = (rf"{BASE_PATTERN}"
               rf"(/(?:\w\w/(?:pic|gif|video)s|pin)/\d+/?)(?!.*#related$)")
    example = "https://www.sex.com/pin/12345-TITLE/"

    def pins(self):
        return (self.root + self.groups[0],)


class SexcomRelatedPinExtractor(SexcomPinExtractor):
    """Extractor for related pins on www.sex.com"""
    subcategory = "related-pin"
    directory_fmt = ("{category}", "related {original_pin[pin_id]}")
    pattern = rf"{BASE_PATTERN}(/pin/(\d+)/?).*#related$"
    example = "https://www.sex.com/pin/12345#related"

    def metadata(self):
        pin = self._parse_pin(SexcomPinExtractor.pins(self)[0])
        return {"original_pin": pin}

    def pins(self):
        url = (f"{self.root}/pin/related?pinId={self.groups[1]}"
               f"&limit=24&offset=0")
        return self._pagination(url)


class SexcomPinsExtractor(SexcomExtractor):
    """Extractor for a user's pins on www.sex.com"""
    subcategory = "pins"
    directory_fmt = ("{category}", "{user}")
    pattern = rf"{BASE_PATTERN}/user/([^/?#]+)/pins/"
    example = "https://www.sex.com/user/USER/pins/"

    def metadata(self):
        return {"user": text.unquote(self.groups[0])}

    def pins(self):
        url = f"{self.root}/user/{self.groups[0]}/pins/"
        return self._pagination(url)


class SexcomLikesExtractor(SexcomExtractor):
    """Extractor for a user's liked pins on www.sex.com"""
    subcategory = "likes"
    directory_fmt = ("{category}", "{user}", "Likes")
    pattern = rf"{BASE_PATTERN}/user/([^/?#]+)/likes/"
    example = "https://www.sex.com/user/USER/likes/"

    def metadata(self):
        return {"user": text.unquote(self.groups[0])}

    def pins(self):
        url = f"{self.root}/user/{self.groups[0]}/likes/"
        return self._pagination(url)


class SexcomBoardExtractor(SexcomExtractor):
    """Extractor for pins from a board on www.sex.com"""
    subcategory = "board"
    directory_fmt = ("{category}", "{user}", "{board}")
    pattern = (rf"{BASE_PATTERN}/user"
               rf"/([^/?#]+)/(?!(?:following|pins|repins|likes)/)([^/?#]+)")
    example = "https://www.sex.com/user/USER/BOARD/"

    def metadata(self):
        self.user, self.board = self.groups
        return {
            "user" : text.unquote(self.user),
            "board": text.unquote(self.board),
        }

    def pins(self):
        url = f"{self.root}/user/{self.user}/{self.board}/"
        return self._pagination(url)


class SexcomFeedExtractor(SexcomExtractor):
    """Extractor for pins from your account's main feed on www.sex.com"""
    subcategory = "feed"
    directory_fmt = ("{category}", "feed")
    pattern = rf"{BASE_PATTERN}/feed"
    example = "https://www.sex.com/feed/"

    def metadata(self):
        return {"feed": True}

    def pins(self):
        if not self.cookies_check(("sess_sex",)):
            self.log.warning("no 'sess_sex' cookie set")
        url = f"{self.root}/feed/"
        return self._pagination(url)


class SexcomSearchExtractor(SexcomExtractor):
    """Extractor for search results on www.sex.com"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search[search]}")
    pattern = (rf"{BASE_PATTERN}/(?:"
               rf"(pic|gif|video)s(?:\?(search=[^#]+)$|/([^/?#]*))"
               rf"|search/(pic|gif|video)s"
               rf")/?(?:\?([^#]+))?")
    example = "https://www.sex.com/search/pics?query=QUERY"

    def _init(self):
        t1, qs1, search_alt, t2, qs2 = self.groups

        self.params = params = text.parse_query(qs1 or qs2)
        if "query" in params:
            params["search"] = params.pop("query")
        params.setdefault("sexual-orientation", "straight")
        params.setdefault("order", "likeCount")
        params.setdefault("search", search_alt or "")

        self.kwdict["search"] = search = params.copy()
        search["type"] = self.type = t1 or t2

    def items(self):
        root = "https://imagex1.sx.cdn.live"
        type = self.type
        gifs = self.config("gifs", True)

        url = (f"{self.root}/portal/api/"
               f"{'picture' if type == 'pic' else type}s/search")
        params = self.params
        params["page"] = text.parse_int(params.get("page"), 1)
        params["limit"] = 40

        while True:
            data = self.request_json(url, params=params)

            for pin in data["data"]:
                path = pin["uri"]
                pin["pin_id"] = pin.pop("id")
                text.nameext_from_url(path, pin)

                parts = path.rsplit("/", 4)
                try:
                    pin["date_url"] = pin["date"] = dt.datetime(
                        int(parts[1]), int(parts[2]), int(parts[3]))
                except Exception:
                    pass

                if type == "pic":
                    pin["type"] = "picture"
                else:
                    pin["type"] = "gif"
                    if gifs and pin["extension"] == "webp":
                        pin["extension"] = "gif"
                        pin["_fallback"] = (f"{root}{path}",)
                        path = f"{path[:-4]}gif"

                pin["url"] = f"{root}{path}"
                yield Message.Directory, "", pin
                yield Message.Url, pin["url"], pin

            if params["page"] >= data["paging"]["numberOfPages"]:
                break
            params["page"] += 1


def _check_empty(response):
    return response.headers.get("content-length") != "0"
