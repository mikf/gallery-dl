# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pornhub.com/"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?(?:[^.]+\.)?pornhub\.com"


class PornhubExtractor(Extractor):
    """Base class for pornhub extractors"""
    category = "pornhub"
    root = "https://www.pornhub.com"


class PornhubGalleryExtractor(PornhubExtractor):
    """Extractor for image galleries on pornhub.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user}", "{gallery[id]} {gallery[title]}")
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/album/(\d+)"
    test = (
        ("https://www.pornhub.com/album/17218841", {
            "pattern": r"https://\w+.phncdn.com/pics/albums/\d+/\d+/\d+/\d+/",
            "count": 81,
            "keyword": {
                "id": int,
                "num": int,
                "score": int,
                "views": int,
                "caption": str,
                "user": "Unknown",
                "gallery": {
                    "id"   : 17218841,
                    "score": int,
                    "views": int,
                    "tags" : list,
                    "title": "Hentai/Ecchi 41",
                },
            },
        }),
        ("https://www.pornhub.com/album/37180171", {
            "exception": exception.AuthorizationError,
        }),
    )

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.gallery_id = match.group(1)
        self._first = None

    def items(self):
        data = self.metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for num, image in enumerate(self.images(), 1):
            url = image["url"]
            image.update(data)
            image["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        url = "{}/album/{}".format(
            self.root, self.gallery_id)
        extr = text.extract_from(self.request(url).text)

        title = extr("<title>", "</title>")
        score = extr('<div id="albumGreenBar" style="width:', '"')
        views = extr('<div id="viewsPhotAlbumCounter">', '<')
        tags = extr('<div id="photoTagsBox"', '<script')
        self._first = extr('<a href="/photo/', '"')
        title, _, user = title.rpartition(" - ")

        return {
            "user" : text.unescape(user[:-14]),
            "gallery": {
                "id"   : text.parse_int(self.gallery_id),
                "title": text.unescape(title),
                "score": text.parse_int(score.partition("%")[0]),
                "views": text.parse_int(views.partition(" ")[0]),
                "tags" : text.split_html(tags)[2:],
            },
        }

    def images(self):
        url = "{}/album/show_album_json?album={}".format(
            self.root, self.gallery_id)
        response = self.request(url)

        if response.content == b"Permission denied":
            raise exception.AuthorizationError()
        images = response.json()
        key = end = self._first

        while True:
            img = images[key]
            yield {
                "url"    : img["img_large"],
                "caption": img["caption"],
                "id"     : text.parse_int(img["id"]),
                "views"  : text.parse_int(img["times_viewed"]),
                "score"  : text.parse_int(img["vote_percent"]),
            }
            key = img["next"]
            if key == end:
                return


class PornhubUserExtractor(PornhubExtractor):
    """Extractor for all galleries of a pornhub user"""
    subcategory = "user"
    pattern = (BASE_PATTERN + r"/(users|model)/([^/?&#]+)"
               "(?:/photos(?:/(public|private|favorites))?)?/?$")
    test = (
        ("https://www.pornhub.com/users/flyings0l0/photos/public", {
            "pattern": PornhubGalleryExtractor.pattern,
            "count": ">= 6",
        }),
        ("https://www.pornhub.com/users/flyings0l0/"),
        ("https://www.pornhub.com/users/flyings0l0/photos/public"),
        ("https://www.pornhub.com/users/flyings0l0/photos/private"),
        ("https://www.pornhub.com/users/flyings0l0/photos/favorites"),
        ("https://www.pornhub.com/model/bossgirl/photos"),
    )

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.type, self.user, self.cat = match.groups()

    def items(self):
        url = "{}/{}/{}/photos/{}/ajax".format(
            self.root, self.type, self.user, self.cat or "public")
        params = {"page": 1}
        headers = {
            "Referer": url[:-5],
            "X-Requested-With": "XMLHttpRequest",
        }

        data = {"_extractor": PornhubGalleryExtractor}
        yield Message.Version, 1
        while True:
            page = self.request(
                url, method="POST", headers=headers, params=params).text
            if not page:
                return
            for gid in text.extract_iter(page, 'id="albumphoto', '"'):
                yield Message.Queue, self.root + "/album/" + gid, data
            params["page"] += 1
