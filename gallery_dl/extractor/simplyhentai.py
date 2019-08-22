# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://www.simply-hentai.com/"""

from .common import GalleryExtractor
from .. import text, util, exception
import json


class SimplyhentaiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from simply-hentai.com"""
    category = "simplyhentai"
    archive_fmt = "{image_id}"
    root = "https://www.simply-hentai.com"
    pattern = (r"(?:https?://)?(?!videos\.)([\w-]+\.simply-hentai\.com"
               r"(?!/(?:album|gifs?|images?|series)(?:/|$))"
               r"(?:/(?!(?:page|all-pages)(?:/|\.|$))[^/?&#]+)+)")
    test = (
        (("https://original-work.simply-hentai.com"
          "/amazon-no-hiyaku-amazon-elixir"), {
            "url": "258289249990502c3138719cb89e995a60861e49",
            "keyword": "8b2400e4b466e8f46802fa5a6b917d2788bb7e8e",
        }),
        ("https://www.simply-hentai.com/notfound", {
            "exception": exception.GalleryDLException,
        }),
        # custom subdomain
        ("https://pokemon.simply-hentai.com/mao-friends-9bc39"),
        # www subdomain, two path segments
        ("https://www.simply-hentai.com/vocaloid/black-magnet"),
    )

    def __init__(self, match):
        url = "https://" + match.group(1)
        GalleryExtractor.__init__(self, match, url)
        self.session.headers["Referer"] = url

    def metadata(self, page):
        path = text.extract(page, '<a class="preview" href="', '"')[0]
        if not path:
            raise exception.NotFoundError("gallery")
        page = self.request(self.root + path).text
        data = json.loads(text.unescape(text.extract(
            page, 'data-react-class="Reader" data-react-props="', '"')[0]))
        self.manga = manga = data["manga"]

        return {
            "title"     : manga["title"],
            "parody"    : manga["series"]["title"],
            "language"  : manga["language"]["name"],
            "lang"      : util.language_to_code(manga["language"]["name"]),
            "characters": [x["name"] for x in manga["characters"]],
            "tags"      : [x["name"] for x in manga["tags"]],
            "artist"    : [x["name"] for x in manga["artists"]],
            "gallery_id": text.parse_int(text.extract(
                manga["images"][0]["sizes"]["full"], "/Album/", "/")[0]),
            "date"      : text.parse_datetime(
                manga["publish_date"], "%Y-%m-%dT%H:%M:%S.%f%z"),
        }

    def images(self, _):
        return [
            (image["sizes"]["full"], {"image_id": image["id"]})
            for image in self.manga["images"]
        ]
