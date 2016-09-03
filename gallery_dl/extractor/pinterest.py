# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.pinterest.com"""

from .common import Extractor, Message
from .. import text

class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{pin-id}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = PinterestAPI(self.session)

    def data_from_pin(self, pin):
        """Get image url and metadata from a pin-object"""
        img = pin["image"]["original"]
        url = img["url"]
        data = {
            "category": self.category,
            "subcategory": self.subcategory,
            "pin-id": pin["id"],
            "note": pin["note"],
            "width": img["width"],
            "height": img["height"],
        }
        return url, text.nameext_from_url(url, data)


class PinterestPinExtractor(PinterestExtractor):
    """Extract an image from a single pin from https://www.pinterest.com"""
    subcategory = "pin"
    pattern = [r"(?:https?://)?(?:www\.)?pinterest\.com/pin/([^/]+)"]

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
    """Extract an image from a single pin from https://www.pinterest.com"""
    category = "pinterest"
    subcategory = "board"
    directory_fmt = ["{category}", "{user}", "{board}"]
    pattern = [r"(?:https?://)?(?:www\.)?pinterest\.com/(?!pin/)([^/]+)/([^/]+)"]

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
            "category": self.category,
            "subcategory": self.subcategory,
            "user": self.user,
            "board-id": board["id"],
            "board": board["name"],
            "count": board["counts"]["pins"],
        }
        return data


class PinterestAPI():
    """Minimal interface for the pinterest API"""

    def __init__(self, session, access_token="AV2U9Oe6dyC2vfPugUnBvJ7Duxg9FHCJPXPZIvRDXv9hvwBALwAAAAA"):
        self.session = session
        self.session.params["access_token"] = access_token

    def pin(self, pin_id, fields="id,image,note"):
        """Query information about a pin"""
        params = {"fields": fields}
        response = self.session.get(
            "https://api.pinterest.com/v1/pins/{pin}/".format(pin=pin_id),
            params=params
        )
        return self._parse(response)["data"]

    def board(self, user, board, fields="id,name,counts"):
        """Query information about a board"""
        params = {"fields": fields}
        response = self.session.get(
            "https://api.pinterest.com/v1/boards/{user}/{board}/"
            .format(user=user, board=board), params=params
        )
        return self._parse(response)["data"]

    def board_pins(self, user, board, fields="id,image,note"):
        """Yield all pins of a specific board"""
        params = {"fields": fields}
        url = ("https://api.pinterest.com/v1/boards/{user}/{board}/pins/"
               .format(user=user, board=board))
        while True:
            response = self._parse(self.session.get(url, params=params))
            yield from response["data"]

            cursor = response["page"]["cursor"]
            if not cursor:
                return
            params["cursor"] = cursor

    def _parse(self, response):
        """Parse an API response"""
        return response.json()
