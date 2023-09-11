# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://lightroom.adobe.com/"""

from .common import Extractor, Message
from .. import text, util


class LightroomGalleryExtractor(Extractor):
    """Extractor for an image gallery on lightroom.adobe.com"""
    category = "lightroom"
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user}", "{title}")
    filename_fmt = "{num:>04}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?lightroom\.adobe\.com/shares/([0-9a-f]+)"
    example = "https://lightroom.adobe.com/shares/0123456789abcdef"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.href = match.group(1)

    def items(self):
        # Get config
        url = "https://lightroom.adobe.com/shares/" + self.href
        response = self.request(url)
        album = util.json_loads(
            text.extr(response.text, "albumAttributes: ", "\n")
        )

        images = self.images(album)
        for img in images:
            url = img["url"]
            yield Message.Directory, img
            yield Message.Url, url, text.nameext_from_url(url, img)

    def metadata(self, album):
        payload = album["payload"]
        story = payload.get("story") or {}
        return {
            "gallery_id": self.href,
            "user": story.get("author", ""),
            "title": story.get("title", payload["name"]),
        }

    def images(self, album):
        album_md = self.metadata(album)
        base_url = album["base"]
        next_url = album["links"]["/rels/space_album_images_videos"]["href"]
        num = 1

        while next_url:
            url = base_url + next_url
            page = self.request(url).text
            # skip 1st line as it's a JS loop
            data = util.json_loads(page[page.index("\n") + 1:])

            base_url = data["base"]
            for res in data["resources"]:
                img_url, img_size = None, 0
                for key, value in res["asset"]["links"].items():
                    if not key.startswith("/rels/rendition_type/"):
                        continue
                    size = text.parse_int(key.split("/")[-1])
                    if size > img_size:
                        img_size = size
                        img_url = value["href"]

                if img_url:
                    img = {
                        "id": res["asset"]["id"],
                        "num": num,
                        "url": base_url + img_url,
                    }
                    img.update(album_md)
                    yield img
                    num += 1
            try:
                next_url = data["links"]["next"]["href"]
            except KeyError:
                next_url = None
