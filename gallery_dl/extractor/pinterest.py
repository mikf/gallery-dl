# -*- coding: utf-8 -*-

# Copyright 2016-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pinterest.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import itertools
import json

BASE_PATTERN = r"(?:https?://)?(?:\w+\.)?pinterest\.[\w.]+"


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.pinterest.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = PinterestAPI(self)

    def items(self):
        self.api.login()
        data = self.metadata()
        videos = self.config("videos", True)

        yield Message.Directory, data
        for pin in self.pins():

            try:
                media = self._media_from_pin(pin)
            except Exception:
                self.log.debug("Unable to fetch download URL for pin %s",
                               pin.get("id"))
                continue

            if not videos and media.get("duration") is not None:
                continue

            pin.update(data)
            pin.update(media)
            url = media["url"]
            text.nameext_from_url(url, pin)

            if pin["extension"] == "m3u8":
                url = "ytdl:" + url
                pin["extension"] = "mp4"
                pin["_ytdl_extra"] = {"protocol": "m3u8_native"}

            yield Message.Url, url, pin

    def metadata(self):
        """Return general metadata"""

    def pins(self):
        """Return all relevant pin objects"""

    @staticmethod
    def _media_from_pin(pin):
        videos = pin.get("videos")
        if videos:
            video_formats = videos["video_list"]

            for fmt in ("V_HLSV4", "V_HLSV3_WEB", "V_HLSV3_MOBILE"):
                if fmt in video_formats:
                    media = video_formats[fmt]
                    break
            else:
                media = max(video_formats.values(),
                            key=lambda x: x.get("width", 0))

            if "V_720P" in video_formats:
                media["_fallback"] = (video_formats["V_720P"]["url"],)

            return media

        return pin["images"]["orig"]


class PinterestPinExtractor(PinterestExtractor):
    """Extractor for images from a single pin from pinterest.com"""
    subcategory = "pin"
    pattern = BASE_PATTERN + r"/pin/([^/?#&]+)(?!.*#related$)"
    test = (
        ("https://www.pinterest.com/pin/858146903966145189/", {
            "url": "afb3c26719e3a530bb0e871c480882a801a4e8a5",
            "content": ("4c435a66f6bb82bb681db2ecc888f76cf6c5f9ca",
                        "d3e24bc9f7af585e8c23b9136956bd45a4d9b947"),
        }),
        # video pin (#1189)
        ("https://www.pinterest.com/pin/422564377542934214/", {
            "pattern": r"https://v\.pinimg\.com/videos/mc/hls/d7/22/ff"
                       r"/d722ff00ab2352981b89974b37909de8.m3u8",
        }),
        ("https://www.pinterest.com/pin/858146903966145188/", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.pin_id = match.group(1)
        self.pin = None

    def metadata(self):
        self.pin = self.api.pin(self.pin_id)
        return self.pin

    def pins(self):
        return (self.pin,)


class PinterestBoardExtractor(PinterestExtractor):
    """Extractor for images from a board from pinterest.com"""
    subcategory = "board"
    directory_fmt = ("{category}", "{board[owner][username]}", "{board[name]}")
    archive_fmt = "{board[id]}_{id}"
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#&]+)/(?!_saved)([^/?#&]+)/?$"
    test = (
        ("https://www.pinterest.com/g1952849/test-/", {
            "pattern": r"https://i\.pinimg\.com/originals/",
            "count": 2,
        }),
        # board with sections (#835)
        ("https://www.pinterest.com/g1952849/stuff/", {
            "options": (("sections", True),),
            "count": 5,
        }),
        # secret board (#1055)
        ("https://www.pinterest.de/g1952849/secret/", {
            "count": 2,
        }),
        ("https://www.pinterest.com/g1952848/test/", {
            "exception": exception.GalleryDLException,
        }),
        # .co.uk TLD (#914)
        ("https://www.pinterest.co.uk/hextra7519/based-animals/"),
    )

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))
        self.board_name = text.unquote(match.group(2))
        self.board = None

    def metadata(self):
        self.board = self.api.board(self.user, self.board_name)
        return {"board": self.board}

    def pins(self):
        board = self.board

        if board["section_count"] and self.config("sections", True):
            pins = [self.api.board_pins(board["id"])]
            for section in self.api.board_sections(board["id"]):
                pins.append(self.api.board_section_pins(section["id"]))
            return itertools.chain.from_iterable(pins)
        else:
            return self.api.board_pins(board["id"])


class PinterestUserExtractor(PinterestExtractor):
    """Extractor for a user's boards"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#&]+)(?:/_saved)?/?$"
    test = (
        ("https://www.pinterest.de/g1952849/", {
            "pattern": PinterestBoardExtractor.pattern,
            "count": ">= 2",
        }),
        ("https://www.pinterest.de/g1952849/_saved/"),
    )

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))

    def items(self):
        for board in self.api.boards(self.user):
            url = board.get("url")
            if url:
                board["_extractor"] = PinterestBoardExtractor
                yield Message.Queue, self.root + url, board


class PinterestSectionExtractor(PinterestExtractor):
    """Extractor for board sections on pinterest.com"""
    subcategory = "section"
    directory_fmt = ("{category}", "{board[owner][username]}",
                     "{board[name]}", "{section[title]}")
    archive_fmt = "{board[id]}_{id}"
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#&]+)/([^/?#&]+)/([^/?#&]+)"
    test = ("https://www.pinterest.com/g1952849/stuff/section", {
        "count": 2,
    })

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))
        self.board_slug = text.unquote(match.group(2))
        self.section_slug = text.unquote(match.group(3))
        self.section = None

    def metadata(self):
        section = self.section = self.api.board_section(
            self.user, self.board_slug, self.section_slug)
        section.pop("preview_pins", None)
        return {"board": section.pop("board"), "section": section}

    def pins(self):
        return self.api.board_section_pins(self.section["id"])


class PinterestSearchExtractor(PinterestExtractor):
    """Extractor for Pinterest search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = BASE_PATTERN + r"/search/pins/?\?q=([^&#]+)"
    test = ("https://www.pinterest.de/search/pins/?q=nature", {
        "range": "1-50",
        "count": ">= 50",
    })

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.search = match.group(1)

    def metadata(self):
        return {"search": self.search}

    def pins(self):
        return self.api.search(self.search)


class PinterestRelatedPinExtractor(PinterestPinExtractor):
    """Extractor for related pins of another pin from pinterest.com"""
    subcategory = "related-pin"
    directory_fmt = ("{category}", "related {original_pin[id]}")
    pattern = BASE_PATTERN + r"/pin/([^/?#&]+).*#related$"
    test = ("https://www.pinterest.com/pin/858146903966145189/#related", {
        "range": "31-70",
        "count": 40,
        "archive": False,
    })

    def metadata(self):
        return {"original_pin": self.api.pin(self.pin_id)}

    def pins(self):
        return self.api.pin_related(self.pin_id)


class PinterestRelatedBoardExtractor(PinterestBoardExtractor):
    """Extractor for related pins of a board from pinterest.com"""
    subcategory = "related-board"
    directory_fmt = ("{category}", "{board[owner][username]}",
                     "{board[name]}", "related")
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#&]+)/([^/?#&]+)/?#related$"
    test = ("https://www.pinterest.com/g1952849/test-/#related", {
        "range": "31-70",
        "count": 40,
        "archive": False,
    })

    def pins(self):
        return self.api.board_related(self.board["id"])


class PinterestPinitExtractor(PinterestExtractor):
    """Extractor for images from a pin.it URL"""
    subcategory = "pinit"
    pattern = r"(?:https?://)?pin\.it/([^/?#&]+)"

    test = (
        ("https://pin.it/Hvt8hgT", {
            "url": "8daad8558382c68f0868bdbd17d05205184632fa",
        }),
        ("https://pin.it/Hvt8hgS", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.shortened_id = match.group(1)

    def items(self):
        url = "https://api.pinterest.com/url_shortener/{}/redirect".format(
            self.shortened_id)
        response = self.request(url, method="HEAD", allow_redirects=False)
        location = response.headers.get("Location")
        if not location or not PinterestPinExtractor.pattern.match(location):
            raise exception.NotFoundError("pin")
        yield Message.Queue, location, {"_extractor": PinterestPinExtractor}


class PinterestAPI():
    """Minimal interface for the Pinterest Web API

    For a better and more complete implementation in PHP, see
    - https://github.com/seregazhuk/php-pinterest-bot
    """

    BASE_URL = "https://www.pinterest.com"
    HEADERS = {
        "Accept"              : "application/json, text/javascript, "
                                "*/*, q=0.01",
        "Accept-Language"     : "en-US,en;q=0.5",
        "Referer"             : BASE_URL + "/",
        "X-Requested-With"    : "XMLHttpRequest",
        "X-APP-VERSION"       : "31461e0",
        "X-CSRFToken"         : None,
        "X-Pinterest-AppState": "active",
        "Origin"              : BASE_URL,
    }

    def __init__(self, extractor):
        self.extractor = extractor

        csrf_token = util.generate_token()
        self.headers = self.HEADERS.copy()
        self.headers["X-CSRFToken"] = csrf_token
        self.cookies = {"csrftoken": csrf_token}

    def pin(self, pin_id):
        """Query information about a pin"""
        options = {"id": pin_id, "field_set_key": "detailed"}
        return self._call("Pin", options)["resource_response"]["data"]

    def pin_related(self, pin_id):
        """Yield related pins of another pin"""
        options = {"pin": pin_id, "add_vase": True, "pins_only": True}
        return self._pagination("RelatedPinFeed", options)

    def board(self, user, board_name):
        """Query information about a board"""
        options = {"slug": board_name, "username": user,
                   "field_set_key": "detailed"}
        return self._call("Board", options)["resource_response"]["data"]

    def boards(self, user):
        """Yield all boards from 'user'"""
        options = {
            "sort"            : "last_pinned_to",
            "field_set_key"   : "profile_grid_item",
            "filter_stories"  : False,
            "username"        : user,
            "page_size"       : 25,
            "include_archived": True,
        }
        return self._pagination("Boards", options)

    def board_pins(self, board_id):
        """Yield all pins of a specific board"""
        options = {"board_id": board_id}
        return self._pagination("BoardFeed", options)

    def board_section(self, user, board_slug, section_slug):
        """Yield a specific board section"""
        options = {"board_slug": board_slug, "section_slug": section_slug,
                   "username": user}
        return self._call("BoardSection", options)["resource_response"]["data"]

    def board_sections(self, board_id):
        """Yield all sections of a specific board"""
        options = {"board_id": board_id}
        return self._pagination("BoardSections", options)

    def board_section_pins(self, section_id):
        """Yield all pins from a board section"""
        options = {"section_id": section_id}
        return self._pagination("BoardSectionPins", options)

    def board_related(self, board_id):
        """Yield related pins of a specific board"""
        options = {"board_id": board_id, "add_vase": True}
        return self._pagination("BoardRelatedPixieFeed", options)

    def search(self, query):
        """Yield pins from searches"""
        options = {"query": query, "scope": "pins", "rs": "typed"}
        return self._pagination("BaseSearch", options)

    def login(self):
        """Login and obtain session cookies"""
        username, password = self.extractor._get_auth_info()
        if username:
            self.cookies.update(self._login_impl(username, password))

    @cache(maxage=180*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.extractor.log.info("Logging in as %s", username)

        url = self.BASE_URL + "/resource/UserSessionResource/create/"
        options = {
            "username_or_email": username,
            "password"         : password,
        }
        data = {"data": json.dumps({"options": options}), "source_url": ""}

        try:
            response = self.extractor.request(
                url, method="POST", headers=self.headers,
                cookies=self.cookies, data=data)
            resource = response.json()["resource_response"]
        except (exception.HttpError, ValueError, KeyError):
            raise exception.AuthenticationError()

        if resource["status"] != "success":
            raise exception.AuthenticationError()
        return {
            cookie.name: cookie.value
            for cookie in response.cookies
        }

    def _call(self, resource, options):
        url = "{}/resource/{}Resource/get/".format(self.BASE_URL, resource)
        params = {"data": json.dumps({"options": options}), "source_url": ""}

        response = self.extractor.request(
            url, params=params, headers=self.headers,
            cookies=self.cookies, fatal=False)

        try:
            data = response.json()
        except ValueError:
            data = {}

        if response.status_code < 400 and not response.history:
            return data

        if response.status_code == 404 or response.history:
            resource = self.extractor.subcategory.rpartition("-")[2]
            raise exception.NotFoundError(resource)
        self.extractor.log.debug("Server response: %s", response.text)
        raise exception.StopExtraction("API request failed")

    def _pagination(self, resource, options):
        while True:
            data = self._call(resource, options)
            results = data["resource_response"]["data"]
            if isinstance(results, dict):
                results = results["results"]
            yield from results

            try:
                bookmarks = data["resource"]["options"]["bookmarks"]
                if (not bookmarks or bookmarks[0] == "-end-" or
                        bookmarks[0].startswith("Y2JOb25lO")):
                    return
                options["bookmarks"] = bookmarks
            except KeyError:
                return
