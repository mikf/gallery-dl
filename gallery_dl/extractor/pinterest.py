# -*- coding: utf-8 -*-

# Copyright 2016-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pinterest.com/"""

from .common import Extractor, Message
from .. import text, exception
import itertools
import json


BASE_PATTERN = r"(?:https?://)?(?:\w+\.)?pinterest\.[\w.]+"


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = PinterestAPI(self)

    def items(self):
        data = self.metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        for pin in self.pins():
            if "images" in pin:
                url, pin_data = self.data_from_pin(pin)
                pin_data.update(data)
                yield Message.Url, url, pin_data

    def metadata(self):
        """Return general metadata"""

    def pins(self):
        """Return all relevant pin-objects"""

    @staticmethod
    def data_from_pin(pin):
        """Get image url and metadata from a pin-object"""
        img = pin["images"]["orig"]
        url = img["url"]
        pin["width"] = img["width"]
        pin["height"] = img["height"]
        return url, text.nameext_from_url(url, pin)


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
        return self.data_from_pin(self.pin)[1]

    def pins(self):
        return (self.pin,)


class PinterestBoardExtractor(PinterestExtractor):
    """Extractor for images from a board from pinterest.com"""
    subcategory = "board"
    directory_fmt = ("{category}", "{board[owner][username]}", "{board[name]}")
    archive_fmt = "{board[id]}_{id}"
    pattern = BASE_PATTERN + r"/(?!pin/)([^/?#&]+)/([^/?#&]+)/?$"
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
        pin = self.api.pin(self.pin_id)
        return {"original_pin": self.data_from_pin(pin)[1]}

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
        "X-Pinterest-AppState": "active",
        "X-APP-VERSION"       : "b00dd49",
        "X-Requested-With"    : "XMLHttpRequest",
        "Origin"              : BASE_URL,
        "Referer"             : BASE_URL + "/",
    }

    def __init__(self, extractor):
        self.extractor = extractor

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

    def _call(self, resource, options):
        url = "{}/resource/{}Resource/get/".format(self.BASE_URL, resource)
        params = {"data": json.dumps({"options": options}), "source_url": ""}

        response = self.extractor.request(
            url, params=params, headers=self.HEADERS, fatal=False)

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
            yield from data["resource_response"]["data"]

            try:
                bookmarks = data["resource"]["options"]["bookmarks"]
                if (not bookmarks or bookmarks[0] == "-end-" or
                        bookmarks[0].startswith("Y2JOb25lO")):
                    return
                options["bookmarks"] = bookmarks
            except KeyError:
                return
