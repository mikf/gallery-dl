# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pinterest.com/"""

from .common import Extractor, Message
from .. import text, util, exception
import itertools

BASE_PATTERN = r"(?:https?://)?(?:\w+\.)?pinterest\.[\w.]+"


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{id}{media_id:?_//}.{extension}"
    archive_fmt = "{id}{media_id}"
    root = "https://www.pinterest.com"

    def _init(self):
        domain = self.config("domain")
        if not domain or domain == "auto" :
            self.root = text.root_from_url(self.url)
        else:
            self.root = text.ensure_http_scheme(domain)

        self.api = PinterestAPI(self)

    def items(self):
        data = self.metadata()
        videos = self.config("videos", True)

        yield Message.Directory, data
        for pin in self.pins():

            if isinstance(pin, tuple):
                url, data = pin
                yield Message.Queue, url, data
                continue

            pin.update(data)

            carousel_data = pin.get("carousel_data")
            if carousel_data:
                pin["count"] = len(carousel_data["carousel_slots"])
                for num, slot in enumerate(carousel_data["carousel_slots"], 1):
                    slot["media_id"] = slot.pop("id")
                    pin.update(slot)
                    pin["num"] = num
                    size, image = next(iter(slot["images"].items()))
                    url = image["url"].replace("/" + size + "/", "/originals/")
                    yield Message.Url, url, text.nameext_from_url(url, pin)

            else:
                try:
                    media = self._media_from_pin(pin)
                except Exception:
                    self.log.debug("Unable to fetch download URL for pin %s",
                                   pin.get("id"))
                    continue

                if videos or media.get("duration") is None:
                    pin.update(media)
                    pin["num"] = pin["count"] = 1
                    pin["media_id"] = ""

                    url = media["url"]
                    text.nameext_from_url(url, pin)

                    if pin["extension"] == "m3u8":
                        url = "ytdl:" + url
                        pin["extension"] = "mp4"

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
    pattern = BASE_PATTERN + r"/pin/([^/?#]+)(?!.*#related$)"
    example = "https://www.pinterest.com/pin/12345/"

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
    pattern = (BASE_PATTERN + r"/(?!pin/)([^/?#]+)"
               "/(?!_saved|_created|pins/)([^/?#]+)/?$")
    example = "https://www.pinterest.com/USER/BOARD/"

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
        pins = self.api.board_pins(board["id"])

        if board["section_count"] and self.config("sections", True):
            base = "{}{}id:".format(self.root, board["url"])
            data = {"_extractor": PinterestSectionExtractor}
            sections = [(base + section["id"], data)
                        for section in self.api.board_sections(board["id"])]
            pins = itertools.chain(pins, sections)

        return pins


class PinterestUserExtractor(PinterestExtractor):
    """Extractor for a user's boards"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#]+)(?:/_saved)?/?$"
    example = "https://www.pinterest.com/USER/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))

    def items(self):
        for board in self.api.boards(self.user):
            url = board.get("url")
            if url:
                board["_extractor"] = PinterestBoardExtractor
                yield Message.Queue, self.root + url, board


class PinterestAllpinsExtractor(PinterestExtractor):
    """Extractor for a user's 'All Pins' feed"""
    subcategory = "allpins"
    directory_fmt = ("{category}", "{user}")
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#]+)/pins/?$"
    example = "https://www.pinterest.com/USER/pins/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))

    def metadata(self):
        return {"user": self.user}

    def pins(self):
        return self.api.user_pins(self.user)


class PinterestCreatedExtractor(PinterestExtractor):
    """Extractor for a user's created pins"""
    subcategory = "created"
    directory_fmt = ("{category}", "{user}")
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#]+)/_created/?$"
    example = "https://www.pinterest.com/USER/_created/"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))

    def metadata(self):
        return {"user": self.user}

    def pins(self):
        return self.api.user_activity_pins(self.user)


class PinterestSectionExtractor(PinterestExtractor):
    """Extractor for board sections on pinterest.com"""
    subcategory = "section"
    directory_fmt = ("{category}", "{board[owner][username]}",
                     "{board[name]}", "{section[title]}")
    archive_fmt = "{board[id]}_{id}"
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#]+)/([^/?#]+)/([^/?#]+)"
    example = "https://www.pinterest.com/USER/BOARD/SECTION"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.user = text.unquote(match.group(1))
        self.board_slug = text.unquote(match.group(2))
        self.section_slug = text.unquote(match.group(3))
        self.section = None

    def metadata(self):
        if self.section_slug.startswith("id:"):
            section = self.section = self.api.board_section(
                self.section_slug[3:])
        else:
            section = self.section = self.api.board_section_by_name(
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
    example = "https://www.pinterest.com/search/pins/?q=QUERY"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.search = text.unquote(match.group(1))

    def metadata(self):
        return {"search": self.search}

    def pins(self):
        return self.api.search(self.search)


class PinterestRelatedPinExtractor(PinterestPinExtractor):
    """Extractor for related pins of another pin from pinterest.com"""
    subcategory = "related-pin"
    directory_fmt = ("{category}", "related {original_pin[id]}")
    pattern = BASE_PATTERN + r"/pin/([^/?#]+).*#related$"
    example = "https://www.pinterest.com/pin/12345/#related"

    def metadata(self):
        return {"original_pin": self.api.pin(self.pin_id)}

    def pins(self):
        return self.api.pin_related(self.pin_id)


class PinterestRelatedBoardExtractor(PinterestBoardExtractor):
    """Extractor for related pins of a board from pinterest.com"""
    subcategory = "related-board"
    directory_fmt = ("{category}", "{board[owner][username]}",
                     "{board[name]}", "related")
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#]+)/([^/?#]+)/?#related$"
    example = "https://www.pinterest.com/USER/BOARD/#related"

    def pins(self):
        return self.api.board_content_recommendation(self.board["id"])


class PinterestPinitExtractor(PinterestExtractor):
    """Extractor for images from a pin.it URL"""
    subcategory = "pinit"
    pattern = r"(?:https?://)?pin\.it/([^/?#]+)"
    example = "https://pin.it/abcde"

    def __init__(self, match):
        PinterestExtractor.__init__(self, match)
        self.shortened_id = match.group(1)

    def items(self):
        url = "https://api.pinterest.com/url_shortener/{}/redirect/".format(
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

    def __init__(self, extractor):
        csrf_token = util.generate_token()

        self.extractor = extractor
        self.root = extractor.root
        self.cookies = {"csrftoken": csrf_token}
        self.headers = {
            "Accept"              : "application/json, text/javascript, "
                                    "*/*, q=0.01",
            "Accept-Language"     : "en-US,en;q=0.5",
            "X-Requested-With"    : "XMLHttpRequest",
            "X-APP-VERSION"       : "0c4af40",
            "X-CSRFToken"         : csrf_token,
            "X-Pinterest-AppState": "active",
            "Origin"              : self.root,
        }

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

    def board_section(self, section_id):
        """Yield a specific board section"""
        options = {"section_id": section_id}
        return self._call("BoardSection", options)["resource_response"]["data"]

    def board_section_by_name(self, user, board_slug, section_slug):
        """Yield a board section by name"""
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

    def board_content_recommendation(self, board_id):
        """Yield related pins of a specific board"""
        options = {"id": board_id, "type": "board", "add_vase": True}
        return self._pagination("BoardContentRecommendation", options)

    def user_pins(self, user):
        """Yield all pins from 'user'"""
        options = {
            "is_own_profile_pins": False,
            "username"           : user,
            "field_set_key"      : "grid_item",
            "pin_filter"         : None,
        }
        return self._pagination("UserPins", options)

    def user_activity_pins(self, user):
        """Yield pins created by 'user'"""
        options = {
            "exclude_add_pin_rep": True,
            "field_set_key"      : "grid_item",
            "is_own_profile_pins": False,
            "username"           : user,
        }
        return self._pagination("UserActivityPins", options)

    def search(self, query):
        """Yield pins from searches"""
        options = {"query": query, "scope": "pins", "rs": "typed"}
        return self._pagination("BaseSearch", options)

    def _call(self, resource, options):
        url = "{}/resource/{}Resource/get/".format(self.root, resource)
        params = {
            "data"      : util.json_dumps({"options": options}),
            "source_url": "",
        }

        response = self.extractor.request(
            url, params=params, headers=self.headers,
            cookies=self.cookies, fatal=False)

        try:
            data = response.json()
        except ValueError:
            data = {}

        if response.history:
            self.root = text.root_from_url(response.url)
        if response.status_code < 400:
            return data
        if response.status_code == 404:
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
