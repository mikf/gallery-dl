# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.pinterest.com"""

from .common import Extractor, Message
from .. import text, exception
import json


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{id}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = PinterestAPI(self)

    def data_from_pin(self, pin):
        """Get image url and metadata from a pin-object"""
        img = pin["images"]["orig"]
        url = img["url"]
        pin["width"] = img["width"]
        pin["height"] = img["height"]
        return url, text.nameext_from_url(url, pin)


class PinterestPinExtractor(PinterestExtractor):
    """Extractor for images from a single pin from pinterest.com"""
    subcategory = "pin"
    pattern = [r"(?:https?://)?(?:[^./]+\.)?pinterest\.[^/]+/pin/([^/?#&]+)"]
    test = [
        ("https://www.pinterest.com/pin/858146903966145189/", {
            "url": "afb3c26719e3a530bb0e871c480882a801a4e8a5",
            "content": "d3e24bc9f7af585e8c23b9136956bd45a4d9b947",
        }),
        ("https://www.pinterest.com/pin/858146903966145188/", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PinterestExtractor.__init__(self)
        self.pin_id = match.group(1)

    def items(self):
        pin = self.api.pin(self.pin_id)
        url, data = self.data_from_pin(pin)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class PinterestBoardExtractor(PinterestExtractor):
    """Extractor for images from a board from pinterest.com"""
    subcategory = "board"
    directory_fmt = ["{category}", "{board[owner][username]}", "{board[name]}"]
    archive_fmt = "{board[id]}_{id}"
    pattern = [r"(?:https?://)?(?:[^./]+\.)?pinterest\.[^/]+/"
               r"(?!pin/)([^/?#&]+)/([^/?#&]+)"]
    test = [
        ("https://www.pinterest.com/g1952849/test-/", {
            "url": "85911dfca313f3f7f48c2aa0bc684f539d1d80a6",
        }),
        ("https://www.pinterest.com/g1952848/test/", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PinterestExtractor.__init__(self)
        self.user, self.board = match.groups()

    def items(self):
        board = self.api.board(self.user, self.board)
        data = {"board": board, "count": board["pin_count"]}
        num = data["count"]
        yield Message.Version, 1
        yield Message.Directory, data
        for pin in self.api.board_pins(board["id"]):
            url, pdata = self.data_from_pin(pin)
            data.update(pdata)
            data["num"] = num
            num -= 1
            yield Message.Url, url, data


class PinterestPinitExtractor(PinterestExtractor):
    """Extractor for images from a pin.it URL"""
    subcategory = "pinit"
    pattern = [r"(?:https?://)?(pin\.it/[^/?#&]+)"]
    test = [
        ("https://pin.it/Hvt8hgT", {
            "url": "8daad8558382c68f0868bdbd17d05205184632fa",
        }),
        ("https://pin.it/Hvt8hgS", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PinterestExtractor.__init__(self)
        self.url = "https://" + match.group(1)

    def items(self):
        response = self.session.head(self.url)
        location = response.headers.get("Location")
        if not location or location in ("https://api.pinterest.com/None",
                                        "https://www.pinterest.com"):
            raise exception.NotFoundError("pin")
        yield Message.Queue, location, {}


class PinterestAPI():
    """Minimal interface for the Pinterest Web API

    For a better and more complete implementation in PHP, see
    - https://github.com/seregazhuk/php-pinterest-bot
    """

    BASE_URL = "https://uk.pinterest.com"
    HEADERS = {
        "Accept"              : "application/json, text/javascript, "
                                "*/*, q=0.01",
        "Accept-Language"     : "en-US,en;q=0.5",
        "X-Pinterest-AppState": "active",
        "X-APP-VERSION"       : "cb1c7f9",
        "X-Requested-With"    : "XMLHttpRequest",
        "Origin"              : BASE_URL + "/",
    }

    def __init__(self, extractor):
        self.log = extractor.log
        self.session = extractor.session

    def pin(self, pin_id):
        """Query information about a pin"""
        options = {"id": pin_id, "field_set_key": "detailed"}
        return self._call("Pin", options)["resource_response"]["data"]

    def board(self, user, board):
        """Query information about a board"""
        options = {"slug": board, "username": user,
                   "field_set_key": "detailed"}
        return self._call("Board", options)["resource_response"]["data"]

    def board_pins(self, board_id):
        """Yield all pins of a specific board"""
        options = {"board_id": board_id}
        return self._pagination("BoardFeed", options)

    def _call(self, resource, options):
        url = "{}/resource/{}Resource/get".format(self.BASE_URL, resource)
        params = {
            "source_url": "",
            "data": json.dumps({"options": options}),
        }

        response = self.session.get(url, params=params, headers=self.HEADERS)
        data = response.json()

        if 200 <= response.status_code < 400 and "resource_response" in data:
            return data

        try:
            msg = data["resource_response"]["error"]["message"]
        except KeyError:
            msg = ""
        if response.status_code == 404:
            msg = msg.partition(" ")[0].lower()
            raise exception.NotFoundError(msg)
        self.log.error("API request failed: %s", msg)
        raise exception.StopExtraction()

    def _pagination(self, resource, options, bookmarks=None):
        while True:
            if bookmarks:
                options["bookmarks"] = bookmarks
            data = self._call(resource, options)
            yield from data["resource_response"]["data"]

            try:
                bookmarks = data["resource"]["options"]["bookmarks"]
                if not bookmarks or bookmarks[0] == "-end-":
                    return
            except KeyError:
                return
