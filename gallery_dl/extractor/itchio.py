# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://itch.io/"""

from .common import Extractor, Message
from .. import text


class ItchioGameExtractor(Extractor):
    """Extractor for itch.io games"""
    category = "itchio"
    subcategory = "game"
    root = "https://itch.io"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{game[title]} ({id}).{extension}"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?(\w+)\.itch\.io/([\w-]+)"
    example = "https://USER.itch.io/GAME"

    def __init__(self, match):
        self.user, self.slug = match.groups()
        Extractor.__init__(self, match)

    def items(self):
        game_url = f"https://{self.user}.itch.io/{self.slug}"
        page = self.request(game_url).text

        params = {
            "source": "view_game",
            "as_props": "1",
            "after_download_lightbox": "true",
        }
        headers = {
            "Referer": game_url,
            "X-Requested-With": "XMLHttpRequest",
            "Origin": f"https://{self.user}.itch.io",
        }
        data = {
            "csrf_token": text.unquote(self.cookies["itchio_token"]),
        }

        for upload_id in text.extract_iter(page, 'data-upload_id="', '"'):
            file_url = f"{game_url}/file/{upload_id}"
            info = self.request_json(file_url, method="POST", params=params,
                                     headers=headers, data=data)

            game = info["lightbox"]["game"]
            user = info["lightbox"]["user"]
            game["url"] = game_url
            user.pop("follow_button", None)
            game = {"game": game, "user": user, "id": upload_id}

            url = info["url"]
            yield Message.Directory, game
            yield Message.Url, url, text.nameext_from_url(url, game)
