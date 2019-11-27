# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.behance.net/"""

from .common import Extractor, Message
from .. import text
import json


class BehanceExtractor(Extractor):
    """Base class for behance extractors"""
    category = "behance"
    root = "https://www.behance.net"

    def items(self):
        yield Message.Version, 1
        for gallery in self.galleries():
            gallery["_extractor"] = BehanceGalleryExtractor
            yield Message.Queue, gallery["url"], self._update(gallery)

    def galleries(self):
        """Return all relevant gallery URLs"""

    @staticmethod
    def _update(data):
        # compress data to simple lists
        if data["fields"] and isinstance(data["fields"][0], dict):
            data["fields"] = [field["name"] for field in data["fields"]]
        data["owners"] = [owner["display_name"] for owner in data["owners"]]

        tags = data.get("tags") or ()
        if tags and isinstance(tags[0], dict):
            tags = [tag["title"] for tag in tags]
        data["tags"] = tags

        # backwards compatibility
        data["gallery_id"] = data["id"]
        data["title"] = data["name"]
        data["user"] = ", ".join(data["owners"])

        return data


class BehanceGalleryExtractor(BehanceExtractor):
    """Extractor for image galleries from www.behance.net"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{owners:J, }", "{id} {name}")
    filename_fmt = "{category}_{id}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/gallery/(\d+)"
    test = (
        ("https://www.behance.net/gallery/17386197/A-Short-Story", {
            "count": 2,
            "url": "ab79bd3bef8d3ae48e6ac74fd995c1dfaec1b7d2",
            "keyword": {
                "id": 17386197,
                "name": 're:"Hi". A short story about the important things ',
                "owners": ["Place Studio", "Julio César Velazquez"],
                "fields": ["Animation", "Character Design", "Directing"],
                "tags": list,
                "module": dict,
            },
        }),
        ("https://www.behance.net/gallery/21324767/Nevada-City", {
            "count": 6,
            "url": "0258fe194fe7d828d6f2c7f6086a9a0a4140db1d",
            "keyword": {"owners": ["Alex Strohl"]},
        }),
        # 'media_collection' modules
        ("https://www.behance.net/gallery/88276087/Audi-R8-RWD", {
            "count": 20,
            "url": "6bebff0d37f85349f9ad28bd8b76fd66627c1e2f",
        }),
    )

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.gallery_id = match.group(1)

    def items(self):
        data = self.get_gallery_data()
        imgs = self.get_images(data)
        data["count"] = len(imgs)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], (url, module) in enumerate(imgs, 1):
            data["module"] = module
            data["extension"] = text.ext_from_url(url)
            yield Message.Url, url, data

    def get_gallery_data(self):
        """Collect gallery info dict"""
        url = "{}/gallery/{}/a".format(self.root, self.gallery_id)
        cookies = {
            "_evidon_consent_cookie":
                '{"consent_date":"2019-01-31T09:41:15.132Z"}',
            "bcp": "815b5eee-8bdf-4898-ac79-33c2bcc0ed19",
            "gk_suid": "66981391",
            "gki": '{"feature_project_view":false,'
                   '"feature_discover_login_prompt":false,'
                   '"feature_project_login_prompt":false}',
            "ilo0": "true",
        }
        page = self.request(url, cookies=cookies).text

        data = json.loads(text.extract(
            page, 'id="beconfig-store_state">', '</script>')[0])
        return self._update(data["project"]["project"])

    @staticmethod
    def get_images(data):
        """Extract image results from an API response"""
        result = []
        append = result.append

        for module in data["modules"]:
            mtype = module["type"]

            if mtype == "image":
                url = module["sizes"]["original"]
                append((url, module))

            elif mtype == "media_collection":
                for component in module["components"]:
                    url = component["sizes"]["source"]
                    append((url, module))

            elif mtype == "embed":
                embed = module.get("original_embed") or module.get("embed")
                if embed:
                    url = "ytdl:" + text.extract(embed, 'src="', '"')[0]
                    append((url, module))

        return result


class BehanceUserExtractor(BehanceExtractor):
    """Extractor for a user's galleries from www.behance.net"""
    subcategory = "user"
    categorytransfer = True
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/([^/?&#]+)/?$"
    test = ("https://www.behance.net/alexstrohl", {
        "count": ">= 8",
        "pattern": BehanceGalleryExtractor.pattern,
    })

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.user = match.group(1)

    def galleries(self):
        url = "{}/{}/projects".format(self.root, self.user)
        params = {"offset": 0}
        headers = {"X-Requested-With": "XMLHttpRequest"}

        while True:
            data = self.request(url, params=params, headers=headers).json()
            work = data["profile"]["activeSection"]["work"]
            yield from work["projects"]
            if not work["hasMore"]:
                return
            params["offset"] += len(work["projects"])


class BehanceCollectionExtractor(BehanceExtractor):
    """Extractor for a collection's galleries from www.behance.net"""
    subcategory = "collection"
    categorytransfer = True
    pattern = r"(?:https?://)?(?:www\.)?behance\.net/collection/(\d+)"
    test = ("https://www.behance.net/collection/71340149/inspiration", {
        "count": ">= 145",
        "pattern": BehanceGalleryExtractor.pattern,
    })

    def __init__(self, match):
        BehanceExtractor.__init__(self, match)
        self.collection_id = match.group(1)

    def galleries(self):
        url = "{}/collection/{}/a".format(self.root, self.collection_id)
        params = {"offset": 0}
        headers = {"X-Requested-With": "XMLHttpRequest"}

        while True:
            data = self.request(url, params=params, headers=headers).json()
            for item in data["items"]:
                yield item["project"]
            if len(data["items"]) < 40:
                return
            params["offset"] += len(data["items"])
