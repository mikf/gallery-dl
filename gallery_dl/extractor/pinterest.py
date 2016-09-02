# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.pinterest.com"""

from .common import Extractor, Message
from .. import text

class PinterestPinExtractor(Extractor):
    """Extract an image from a single pin from https://www.pinterest.com"""
    category = "pinterest"
    subcategory = "pin"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{id}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?pinterest\.com/pin/([^/]+)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.pin_id = match.group(1)
        self.api = PinterestAPI(self.session)

    def items(self):
        pin = self.api.pin(self.pin_id)
        img = pin["image"]["original"]
        data = {
            "category": self.category,
            "subcategory": self.subcategory,
            "id": pin["id"],
            "note": pin["note"],
            "width": img["width"],
            "height": img["height"],
        }
        text.nameext_from_url(img["url"], data)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, img["url"], data


class PinterestAPI():
    """Minimal interface for the pinterest API"""

    def __init__(self, session, access_token="AV2U9Oe6dyC2vfPugUnBvJ7Duxg9FHCJPXPZIvRDXv9hvwBALwAAAAA"):
        self.session = session
        self.session.params["access_token"] = access_token

    def pin(self, pin_id, fields="image,note"):
        """Query information about a pin"""
        params = {"fields": fields}
        response = self.session.get(
            "https://api.pinterest.com/v1/pins/{pin}/".format(pin=pin_id),
            params=params
        )
        return self._parse(response)["data"]

    def board_pins(self, user, board, fields="image,note"):
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
