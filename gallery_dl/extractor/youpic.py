# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://youpic.com"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?youpic\.com"
USER_PATTERN = BASE_PATTERN + r"/photographer/([^/]+)"
IMAGE_PATTERN = BASE_PATTERN + r"/image/(\d+)"


class YoupicExtractor(Extractor):
    category = "youpic"
    directory_fmt = ("{category}", "{user[displayName]}")
    filename_fmt = "{id}_{title}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)

        self.page_state = self._load_page_state()
        self.user = next(iter(self.page_state["redux"]["User"].values()))
        assert self.user is not None, "failed to extract user from page state"

    def _load_page_state(self):
        extr = text.extract_from(self.request(self.url).text)
        return util.json_loads(
            extr('<script id="state" type="application/json">', "<"))

    def _yield_image(self, image):
        url = text.urljoin(image["url"]["url"], "huge/" + image["url"]["file"])

        image["title"] = image["title"].strip()
        image["_mtime"] = image["created"] / 1000

        yield Message.Directory, {**image, "user": self.user}
        yield Message.Url, url, text.nameext_from_url(url, image)


class YoupicUserExtractor(YoupicExtractor):
    subcategory = "user"
    api_root = "https://api3.youpic.com"
    pattern = USER_PATTERN

    def items(self):
        for image in self.images():
            yield from self._yield_image(image)

    def images(self):
        api_url = self.api_root + "/user/" + self.user["id"] + "/newest"
        params = {
            "count": "30",
            "direction": "from",
        }

        while True:
            data = self.request(api_url, params=params).json()

            if data["cursor"] == "":
                break

            yield from data["resource"]["Image"]

            params["cursor"] = data["cursor"]


class YoupicImageExtractor(YoupicExtractor):
    subcategory = "image"
    pattern = IMAGE_PATTERN

    def __init__(self, match):
        YoupicExtractor.__init__(self, match)

        self.image_id = match[1]

    def items(self):
        image = self.page_state["redux"]["Image"][self.image_id]
        yield from self._yield_image(image)
