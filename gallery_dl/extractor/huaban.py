# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pinterest.com/"""

from .common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:\w+\.)?huaban\.com"


class BaseExtractor(Extractor):
    """Base class for other extractors"""

    category = "huaban"
    root = "https://huaban.com"
    api_root = "https://api.huaban.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.url = match.group(0)
        self.id = match.group(1)

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {"category": "huaban"}

    def api_request(self, url, *args, **kwargs):
        default_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;\
q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://huaban.com",
        }
        kwargs.update({"headers": default_headers})
        return self.request(self.api_root + url, *args, **kwargs)

    def pin_img_url(self, pin):
        """real image url from  pin's data"""
        return "https://%s.huaban.com/%s" % (
            pin["file"]["bucket"],
            pin["file"]["key"],
        )


class HuabanPinExtractor(BaseExtractor):
    """Extractor for image from a pin"""

    subcategory = "pin"
    pattern = BASE_PATTERN + "/pins/([0-9]+)"
    directory_fmt = ("{category}",)
    test = ("https://huaban.com/pins/4535272056",)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)

    def items(self):
        metadata = self.api_request(
            "/pins/" + self.id, headers={"Referer": self.url}
        ).json()
        pin = metadata["pin"]
        yield Message.Directory, pin

        pin["filename"] = pin["file"]["key"]
        pin["extension"] = pin["file"]["type"].split("/")[-1]

        yield Message.Url, self.pin_img_url(pin), pin


class HuabanBoardExtractor(BaseExtractor):
    """Extractor for images from a board"""

    subcategory = "board"
    pattern = BASE_PATTERN + "/boards/([0-9]+)"
    directory_fmt = (
        "{category}",
        "{user[user_id]} {user[username]}",
        "{board_id} {title}",
    )

    test = ("https://huaban.com/boards/76275185",)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)

    def items(self):
        metadata = self.api_request(
            "/boards/" + self.id, headers={"Referer": self.url}
        ).json()
        yield Message.Directory, metadata["board"]

        # get all pins
        pins_data = self.api_request(
            "/boards/%s/pins?limit=20" % (self.id),
            headers={"Referer": self.url},
        ).json()
        while True:
            pins = pins_data["pins"]
            if len(pins) <= 0:
                break

            last_pin = None
            for pin in pins:
                pin_file = pin["file"]
                pin["filename"] = pin_file["key"]
                pin["extension"] = pin_file["type"].split("/")[-1]
                yield Message.Url, self.pin_img_url(pin), pin
                last_pin = pin

            pins_data = self.api_request(
                "/boards/%s/pins?limit=20&max=%s"
                % (self.id, last_pin["pin_id"]),
                headers={"Referer": self.url},
            ).json()


class HuabanUserExtractor(BaseExtractor):
    """Extractor for images from  a user's boards"""

    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([\w_]+[_\w\d]*)"
    directory_fmt = ("{category}", "{user_id} {username}")
    test = ("https://huaban.com/user/huaban",)

    def items(self):
        metadata = boards_data = self.api_request(
            "/%s/boards?limit=30&urlname=%s" % (self.id, self.id),
            headers={"Referer": self.url},
        ).json()
        yield Message.Directory, metadata["user"]

        # queue all boards
        while True:
            boards = boards_data["boards"]
            if len(boards) <= 0:
                break

            last_board = None
            for board in boards:
                board["_extractor"] = HuabanBoardExtractor
                yield Message.Queue, "%s/boards/%s" % (
                    self.root,
                    board["board_id"],
                ), {"_extractor": HuabanBoardExtractor}
                last_board = board

            boards_data = self.api_request(
                "/%s/boards?max=%s&limit=30&urlname=%s"
                % (self.id, last_board["board_id"], self.id),
                headers={"Referer": self.url},
            ).json()
