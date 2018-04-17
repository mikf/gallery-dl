# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.pinterest.com"""

from .common import Extractor, Message
from .. import text, util, exception


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{pin_id}.{extension}"
    archive_fmt = "{pin_id}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = PinterestAPI(self)

    def data_from_pin(self, pin):
        """Get image url and metadata from a pin-object"""
        img = pin["image"]["original"]
        url = img["url"]
        data = {
            "pin_id": util.safe_int(pin["id"]),
            "note": pin["note"],
            "width": util.safe_int(img["width"]),
            "height": util.safe_int(img["height"]),
        }
        return url, text.nameext_from_url(url, data)


class PinterestPinExtractor(PinterestExtractor):
    """Extractor for images from a single pin from pinterest.com"""
    subcategory = "pin"
    pattern = [r"(?:https?://)?(?:[^./]+\.)?pinterest\.[^/]+/pin/([^/?#&]+)"]
    test = [
        ("https://www.pinterest.com/pin/858146903966145189/", {
            "url": "afb3c26719e3a530bb0e871c480882a801a4e8a5",
            "keyword": "f651cb271247f306d1d30385d49c7b82da44c2b1",
            "content": "d3e24bc9f7af585e8c23b9136956bd45a4d9b947",
        }),
        ("https://www.pinterest.com/pin/858146903966145188/", {
            "exception": exception.StopExtraction,
        }),
        ("https://www.pinterest.com/pin/85814690396614518/", {
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
    directory_fmt = ["{category}", "{user}", "{board}"]
    pattern = [r"(?:https?://)?(?:[^./]+\.)?pinterest\.[^/]+/"
               r"(?!pin/)([^/?#&]+)/([^/?#&]+)"]
    test = [
        ("https://www.pinterest.com/g1952849/test-/", {
            "url": "85911dfca313f3f7f48c2aa0bc684f539d1d80a6",
            "keyword": "c54cf5aa830994f2ed4871efa7154a5fdaa1c2ce",
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
        data = self.data_from_board(board)
        num = data["count"]
        yield Message.Version, 1
        yield Message.Directory, data
        for pin in self.api.board_pins(self.user, self.board):
            url, pdata = self.data_from_pin(pin)
            data.update(pdata)
            data["num"] = num
            num -= 1
            yield Message.Url, url, data

    def data_from_board(self, board):
        """Get metadata from a board-object"""
        data = {
            "user": self.user,
            "board_id": util.safe_int(board["id"]),
            "board": board["name"],
            "count": board["counts"]["pins"],
        }
        return data


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
    """Minimal interface for the pinterest API"""

    def __init__(self, extractor, access_token=None):
        self.log = extractor.log
        self.session = extractor.session
        self.access_token = (
            access_token or
            extractor.config("access-token") or
            "AfyIXxi1MJ6et0NlIl_vBchHbex-FSWylPyr2GJE2uu3W8A97QAAAAA"
        )

    def pin(self, pin_id, fields="id,image,note"):
        """Query information about a pin"""
        endpoint = "pins/{}/".format(pin_id)
        params = {"fields": fields}
        return self._call(endpoint, params)["data"]

    def board(self, user, board, fields="id,name,counts"):
        """Query information about a board"""
        endpoint = "boards/{}/{}/".format(user, board)
        params = {"fields": fields}
        return self._call(endpoint, params)["data"]

    def board_pins(self, user, board, fields="id,image,note", limit=100):
        """Yield all pins of a specific board"""
        endpoint = "boards/{}/{}/pins/".format(user, board)
        params = {"fields": fields, "limit": limit}
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params):
        params["access_token"] = self.access_token
        url = "https://api.pinterest.com/v1/" + endpoint

        response = self.session.get(url, params=params)
        status = response.status_code
        data = response.json()

        if 200 <= status < 400 and data.get("data"):
            return data

        msg = data.get("message", "")
        if status == 404:
            msg = msg.partition(" ")[0].lower()
            raise exception.NotFoundError(msg)
        self.log.error("API request failed: %s", msg or "")
        raise exception.StopExtraction()

    def _pagination(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)
            yield from response["data"]

            cursor = response["page"]["cursor"]
            if not cursor:
                return
            params["cursor"] = cursor
